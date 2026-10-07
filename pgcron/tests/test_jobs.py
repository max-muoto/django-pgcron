from __future__ import annotations

from typing import TYPE_CHECKING, Any

import pytest
from django.core import management

import pgcron
from pgcron import _jobs
from pgcron.models import Job, JobQuerySet

if TYPE_CHECKING:
    from collections.abc import Callable


def test_all() -> None:
    """Test that the all function works."""
    jobs = _jobs.all()
    assert len(jobs) == 0

    @pgcron.job(pgcron.crontab())
    def test_job():  # type: ignore
        return pgcron.SQLExpression("INSERT INTO name_model (name) VALUES ('test');")

    jobs = _jobs.all()
    # The job is not registered yet
    assert len(jobs) == 0

    management.call_command("pgcron", "sync")
    jobs = _jobs.all()
    assert len(jobs) == 1
    only_job = jobs.pop()
    assert only_job.name == f"{_jobs.JOB_NAME_PREFIX}pgcron.test_job"
    assert only_job.schedule == "* * * * *"
    assert only_job.expression == pgcron.SQLExpression(
        "INSERT INTO name_model (name) VALUES ('test');"
    )


@pytest.mark.django_db(databases=["default", "other"])
def test_all_for_job_in_another_database() -> None:
    """Jobs running against another database are resolved back to their alias."""

    @pgcron.job(pgcron.crontab(), database="other")
    def test_job():
        return pgcron.SQLExpression("SELECT 1;")

    management.call_command("pgcron", "sync")

    jobs = _jobs.all()
    assert len(jobs) == 1
    only_job = jobs.pop()
    assert only_job.name == f"{_jobs.JOB_NAME_PREFIX}pgcron.test_job"
    assert only_job.db_alias == "other"
    assert only_job.database == "other"
    assert only_job.status is _jobs.Status.ENABLED


@pytest.mark.django_db(databases=["default", "other"])
def test_register_and_drop_job_in_another_database() -> None:
    """Jobs running against another database are scheduled/unscheduled in `PGCRON_DATABASE`.

    `pg_cron` can only be installed in a single database, so the `cron` schema doesn't
    exist in the database the job itself runs against.
    """
    job = _jobs.CronJob(
        name=f"{_jobs.JOB_NAME_PREFIX}pgcron.other_db_job",
        expression=pgcron.SQLExpression("SELECT 1;"),
        schedule="* * * * *",
        db_alias="other",
        status=_jobs.Status.ENABLED,
    )
    job.register()
    schedule_job = Job.objects.get()
    assert schedule_job.jobname == job.name
    assert schedule_job.database == "other"

    job.drop()
    assert Job.objects.count() == 0


@pytest.mark.parametrize(
    ("action", "queryset_method"),
    [
        (_jobs.unschedule, "unschedule"),
        (_jobs.enable, "enable"),
        (_jobs.disable, "disable"),
    ],
)
def test_job_actions_query_pgcron_database(
    monkeypatch: pytest.MonkeyPatch,
    settings: Any,
    action: Callable[[str], None],
    queryset_method: str,
) -> None:
    """Job actions query `PGCRON_DATABASE` instead of the default database.

        The `cron` schema only exists in `PGCRON_DATABASE`, which isn't necessarily
    the database the router would pick for the `Job` model.
    """
    # Any aliast other than the router's default will do, no query is run against it.
    settings.PGCRON_DATABASE = "other"
    queried_dbs: list[str | None] = []

    def capture(queryset: JobQuerySet) -> None:
        queried_dbs.append(queryset.db)

    monkeypatch.setattr(JobQuerySet, queryset_method, capture)

    action("pgcron.test_job")

    assert queried_dbs == ["other"]
