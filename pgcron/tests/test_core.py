from __future__ import annotations

import pytest
from django.core import management

import pgcron
import pgcron.schedule
from pgcron._jobs import JOB_NAME_PREFIX
from pgcron.models import Job
from pgcron.tests.models import NameTestModel


@pytest.mark.django_db
def test_synchronous_execution() -> None:
    """Test that we can execute a job synchronously."""

    @pgcron.job(pgcron.crontab())
    def test_job():
        return pgcron.SQLExpression("INSERT INTO name_model (name) VALUES ('test');")

    assert test_job.name == "test_job"
    assert test_job.schedule.to_pgcron_expr() == "* * * * *"
    assert test_job.database == "default"
    with pytest.raises(NotImplementedError):
        test_job()

    test_job.run()
    assert NameTestModel.objects.count() == 1
    assert NameTestModel.objects.get().name == "test"


@pytest.mark.django_db
def test_job_registration() -> None:
    """Test that jobs get properly registered"""

    @pgcron.job(pgcron.crontab())
    def test_job():  # type: ignore
        return pgcron.SQLExpression("INSERT INTO name_model (name) VALUES ('test');")

    management.call_command("pgcron", "sync")
    assert Job.objects.count() == 1
    job = Job.objects.get()
    assert job.command == "INSERT INTO name_model (name) VALUES ('test');"
    assert job.schedule == "* * * * *"
    assert job.nodeport == 5432
    assert job.jobname == f"{JOB_NAME_PREFIX}pgcron.test_job"


@pytest.mark.django_db
def test_custom_job_name() -> None:
    """Test that jobs get properly registered"""

    @pgcron.job(pgcron.crontab(), name="custom_job_name")
    def test_job():  # type: ignore
        return pgcron.SQLExpression("INSERT INTO name_model (name) VALUES ('test');")

    management.call_command("pgcron", "sync")
    assert Job.objects.count() == 1
    assert Job.objects.get().jobname == f"{JOB_NAME_PREFIX}pgcron.custom_job_name"


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("schedule", "expected_expression"),
    [
        (pgcron.seconds(10), "10 seconds"),
        (pgcron.crontab(minute="*/10"), "*/10 * * * *"),
        (pgcron.crontab(hour="*/10"), "* */10 * * *"),
        (pgcron.crontab(day_of_month="*/10"), "* * */10 * *"),
        (pgcron.crontab(month_of_year="*/10"), "* * * */10 *"),
        (pgcron.crontab(day_of_week="*/10"), "* * * * */10"),
    ],
)
def test_time_delta_schedule(schedule: pgcron.schedule.Schedule, expected_expression: str) -> None:
    @pgcron.job(schedule)
    def test_job():  # type: ignore
        return pgcron.SQLExpression("INSERT INTO name_model (name) VALUES ('test');")

    management.call_command("pgcron", "sync")
    assert Job.objects.count() == 1
    job = Job.objects.get()
    assert job.schedule == expected_expression
