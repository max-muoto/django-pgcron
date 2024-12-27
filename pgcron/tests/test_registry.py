from __future__ import annotations

import pgcron
import pgcron._jobs
from pgcron import _registry
from pgcron._jobs import CronJob


def test_register() -> None:
    """Test registering and retrieving jobs."""
    assert _registry.all() == []
    _registry.register(
        name="test_job",
        expression=pgcron.SQLExpression("SELECT 1"),
        schedule="* * * * *",
        database="default",
        app_name="test",
    )
    assert _registry.all() == [
        CronJob(
            name=f"{pgcron._jobs.JOB_NAME_PREFIX}test.test_job",
            expression=pgcron.SQLExpression("SELECT 1"),
            schedule="* * * * *",
            db_alias="default",
            status=pgcron._jobs.Status.DISABLED,
        )
    ]
