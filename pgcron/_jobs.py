"""Internal module for managing pgcron jobs."""

from __future__ import annotations

import dataclasses
from typing import TYPE_CHECKING

from django.conf import settings
from django.db import connections

import pgcron
import pgcron._config
import pgcron.expressions
from pgcron import _compat

if TYPE_CHECKING:
    from django.db.backends.utils import CursorWrapper

    from pgcron.expressions import Expression

JOB_NAME_PREFIX = "pgcron_v1__"
"""Prefix for pgcron jobs."""


class Status(_compat.StrEnum):
    """Status of a pgcron job."""

    ENABLED = "enabled"
    DISABLED = "disabled"


def _get_db_from_alias(alias: str) -> str:
    if not hasattr(settings, "DATABASES"):
        raise RuntimeError("Database settings are not configured.")
    return settings.DATABASES[alias]["NAME"]


def _get_alias_from_db(db: str) -> str:
    if not hasattr(settings, "DATABASES"):
        raise RuntimeError("Database settings are not configured.")

    for alias, database in settings.DATABASES.items():
        if database["NAME"] == db:
            return alias

    raise ValueError(f"Database {db} not found.")


@dataclasses.dataclass(slots=True, frozen=True)
class CronJob:
    """A pgcron job."""

    name: str
    # SQL expression to be executed by the job.
    expression: Expression
    schedule: str
    db_alias: str
    status: Status

    @property
    def database(self) -> str:
        return _get_db_from_alias(self.db_alias)

    @property
    def uri(self) -> str:
        """Gets the ur in the format of "<app_name>.<job_name>"."""
        return self.name.lstrip(JOB_NAME_PREFIX)

    def get_schedule_sql(self, cursor: CursorWrapper) -> str:
        """Return the SQL to schedule the job."""
        return (
            f"SELECT cron.schedule_in_database('{self.name}', '{self.schedule}', "
            f"{self.expression.as_escaped_sql(cursor, self.db_alias)}, '{self.database}');"
        )

    def get_drop_sql(self) -> str:
        """Return the SQL to drop the job."""
        return f"SELECT cron.unschedule('{self.name}');"

    def register(self) -> None:
        """Register the job with pgcron."""
        with connections[pgcron._config.get_database()].cursor() as cursor:
            cursor.execute(self.get_schedule_sql(cursor))

    def drop(self) -> None:
        """Drop the job from pgcron."""
        with connections[self.db_alias].cursor() as cursor:
            cursor.execute(self.get_drop_sql())

    def __eq__(self, other: object) -> bool:
        with connections[self.db_alias].cursor() as cursor:
            return (
                isinstance(other, CronJob)
                and self.name == other.name
                and other.get_schedule_sql(cursor) == self.get_schedule_sql(cursor)
                and self.database == other.database
                and self.schedule == other.schedule
            )

    def __hash__(self) -> int:
        with connections[self.db_alias].cursor() as cursor:
            return hash((self.name, self.get_schedule_sql(cursor), self.database, self.schedule))


def all() -> set[CronJob]:
    """Get all jobs from the database.

    Args:
        database: The database to get jobs from.

    Returns:
        A set of `CronJob` objects representing jobs registered with pgcron
        for the given database.
    """
    from pgcron.models import Job

    pgcron_jobs = (
        Job.objects.using(pgcron._config.get_database())
        .all()
        .filter(jobname__startswith=JOB_NAME_PREFIX)
        .only("jobname", "active", "command", "schedule", "database")
    )
    return {
        CronJob(
            name=job.jobname,
            expression=pgcron.expressions.SQLExpression(job.command),
            schedule=job.schedule,
            db_alias=_get_alias_from_db(job.database),
            status=Status.ENABLED if job.active else Status.DISABLED,
        )
        for job in pgcron_jobs
        if job.jobname is not None
    }


def unschedule(name: str) -> None:
    """Unschedule a pgcron job.

    Args:
        name: The name of the job to unschedule.

    Raises:
        ValueError: If the job is not found.
    """
    from pgcron.models import Job

    Job.objects.filter(jobname=f"{JOB_NAME_PREFIX}{name}").unschedule()


def enable(name: str) -> None:
    """Enable a pgcron job.

    Args:
        name: The name of the job to enable.
    """
    from pgcron.models import Job

    Job.objects.filter(jobname=f"{JOB_NAME_PREFIX}{name}").enable()


def disable(name: str) -> None:
    """Disable a pgcron job.

    Args:
        name: The name of the job to disable.
    """
    from pgcron.models import Job

    Job.objects.filter(jobname=f"{JOB_NAME_PREFIX}{name}").disable()
