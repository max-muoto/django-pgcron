"""Expressions to be executed by pgcron."""

from __future__ import annotations

import abc
from typing import TYPE_CHECKING, Any, ClassVar, Literal, final

from django.db import connections
from django.db.models.sql import DeleteQuery, UpdateQuery

import pgcron._sql

if TYPE_CHECKING:
    from django.db import models
    from django.db.backends.utils import CursorWrapper


class _UpdateAndSetValues(UpdateQuery):
    """An UpdateQuery that has already set the values."""

    update_values: ClassVar[dict[str, Any]]

    def _setup_query(self) -> None:
        super()._setup_query()  # type: ignore
        self.add_update_values(self.update_values)


def _chain_and_mogrify(
    queryset: models.QuerySet[Any],
    cursor: CursorWrapper,
    db: str,
    operation: Literal["delete", "update"],
    kwargs: dict[str, Any] | None = None,
) -> str | bytes:
    """Chain the queryset with the operation and mogrify the result."""
    compiler = queryset.query.get_compiler(using=db)

    if operation == "delete":
        klass = DeleteQuery
    elif operation == "update" and kwargs is not None:
        klass = _UpdateAndSetValues
        klass.update_values = kwargs
    else:
        raise AssertionError("Invalid operation.")

    sql, params = compiler.compile(queryset.query.chain(klass))
    with connections[db].cursor() as cursor:
        return cursor.mogrify(sql, params)


class Expression(abc.ABC):
    """An expression to be executed by pgcron."""

    @abc.abstractmethod
    def as_sql(self, cursor: CursorWrapper, db: str) -> str | bytes:
        """Return the expression as a SQL string or bytes."""

    def as_escaped_sql(self, cursor: CursorWrapper, db: str) -> str | bytes:
        """Escape the expression."""
        sql = self.as_sql(cursor, db)
        return pgcron._sql.escape_sql(sql) if not pgcron._sql.is_escaped(sql) else sql


@final
class SQLExpression(str, Expression):
    """A SQL statement to be executed by pgcron."""

    def as_sql(self, cursor: CursorWrapper | None = None, db: str | None = None) -> str:
        return self


@final
class Delete(Expression):
    """A DELETE statement to be executed by pgcron.

    Examples:
        Delete all users over 100 years old:

        ```python
        pgcron.Delete(User.objects.filter(age__gt=100))
        ```
    """

    def __init__(self, queryset: models.QuerySet[Any]) -> None:
        self.queryset = queryset

    def as_sql(self, cursor: CursorWrapper, db: str) -> str | bytes:
        return _chain_and_mogrify(self.queryset, cursor, db, "delete")


@final
class Update(Expression):
    """An UPDATE statement to be executed by pgcron.

    Examples:
        Update all users over 100 years old:

        ```python
        pgcron.Update(User.objects.filter(age__gt=100), age=100)
        ```
    """

    def __init__(self, queryset: models.QuerySet[Any], **kwargs: Any) -> None:
        self.queryset = queryset
        self.kwargs = kwargs

    def as_sql(self, cursor: CursorWrapper, db: str) -> str | bytes:
        return _chain_and_mogrify(self.queryset, cursor, db, "update", self.kwargs)
