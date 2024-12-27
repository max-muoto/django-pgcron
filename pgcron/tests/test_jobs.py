from __future__ import annotations

from django.core import management

import pgcron
from pgcron import _jobs


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
