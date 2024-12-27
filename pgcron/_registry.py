"""Internal module for tracking registered pgcron jobs."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pgcron import _config, _jobs

if TYPE_CHECKING:
    from pgcron.expressions import Expression


_REGISTRY: dict[str, _jobs.CronJob] = {}
"""Global registry of pgcron jobs."""


def register(
    *,
    name: str,
    expression: Expression,
    schedule: str,
    database: str | None = None,
    app_name: str,
) -> None:
    database = database or _config.get_database()
    uri = f"sql_job://{app_name}.{name}"
    _REGISTRY[uri] = _jobs.CronJob(
        name=f"{_jobs.JOB_NAME_PREFIX}{app_name}.{name}",
        expression=expression,
        schedule=schedule,
        db_alias=database,
        status=_jobs.Status.DISABLED,
    )


def all() -> list[_jobs.CronJob]:
    """Return all registered jobs."""
    return list(_REGISTRY.values())


def clear() -> None:
    """Clear the registry."""
    _REGISTRY.clear()
