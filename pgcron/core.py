from __future__ import annotations

import dataclasses
from typing import TYPE_CHECKING, NoReturn, cast, final

from django.db import connections

import pgcron.schedule
from pgcron import _config, _registry, expressions

if TYPE_CHECKING:
    from collections.abc import Callable


@final
@dataclasses.dataclass(slots=True, frozen=True, repr=False, eq=False)
class Job:
    """A registered pgcron job."""

    name: str
    schedule: pgcron.schedule.Schedule
    expression: expressions.Expression
    database: str

    def __call__(self, *args: object, **kwargs: object) -> NoReturn:
        raise NotImplementedError("Jobs can be not be directly executed")

    def run(self) -> None:
        """Run the job synchronously."""
        with connections[self.database].cursor() as cursor:
            cursor.execute(cast(str, self.expression.as_sql(cursor, self.database)))


def job(
    schedule: pgcron.schedule.Schedule | str,
    *,
    name: str | None = None,
    database: str | None = None,
) -> Callable[[Callable[[], expressions.Expression]], Job]:
    """Register a pgcron job that runs a SQL expression.

    Args:
        schedule: The schedule object or crontab expression for the job.
        name: The name of the job, if None, the name will be the function name.
        database: The database to run the job on.
            Defaults to the database set in `PGCRON_DATABASE` in settings,
            which defaults to Django's default database.

    Returns:
        A decorator that registers the job with pgcron, and returns a `Job` object
        that can be used to run the job synchronously if needed.

    Examples:
        Job that deletes users over 100 years old every minute:
        ```python
        import pgcron


        @pgcron.job("* * * * *")
        def delete_old_users() -> pgcron.SQLExpression:
            return pgcron.SQLExpression("DELETE FROM users WHERE age > 100")
        ```

        Job that vacuums the database every day at 9am:
        ```python
        import pgcron


        @pgcron.job("0 9 * * *")
        def vacuum_db() -> pgcron.SQLExpression:
            return pgcron.SQLExpression("VACUUM")
        ```

        Job that calls a stored procedure every 5 seconds:
        ```python
        import pgcron


        @pgcron.job(pgcron.seconds(5))
        def call_stored_procedure() -> pgcron.SQLExpression:
            return pgcron.SQLExpression("CALL my_stored_procedure()")
        ```
    """

    if isinstance(schedule, str):
        schedule = pgcron.schedule.crontab.from_str(schedule)

    def decorator(func: Callable[[], expressions.Expression]) -> Job:
        app_label = func.__module__.split(".")[0]
        sql = func()
        job_name = name or func.__name__
        db_alias = database or _config.get_database()
        _registry.register(
            name=job_name,
            app_name=app_label,
            expression=sql,
            schedule=schedule.to_pgcron_expr(),
            database=db_alias,
        )
        return Job(name=job_name, schedule=schedule, expression=sql, database=db_alias)

    return decorator
