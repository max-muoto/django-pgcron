from __future__ import annotations

import datetime as dt

import pytest
from django.core import management

import pgcron
from pgcron import _registry
from pgcron._jobs import JOB_NAME_PREFIX
from pgcron.models import Job, JobRunDetails

SELECT_1 = pgcron.SQLExpression("SELECT 1;")


@pytest.mark.django_db
def test_job(current_db: str) -> None:
    """Test that the Job model works as a pass-through."""
    assert Job.objects.count() == 0
    _registry.register(
        name="test_job",
        expression=SELECT_1,
        schedule="* * * * *",
        app_name="test",
    )
    assert Job.objects.count() == 0
    management.call_command("pgcron", "sync")
    assert Job.objects.count() == 1
    scheduled_job = Job.objects.get()
    assert scheduled_job.jobname == f"{JOB_NAME_PREFIX}test.test_job"
    assert scheduled_job.command == "SELECT 1;"
    assert scheduled_job.schedule == "* * * * *"
    assert scheduled_job.database == current_db
    assert scheduled_job.active


def test_job_dunders() -> None:
    """Test the custom dunders for Job."""
    job = Job(
        jobid=1,
        jobname="test_job",
        command="SELECT 1;",
        schedule="* * * * *",
        active=True,
        nodename="localhost",
        nodeport=5432,
        database="test_db",
        username="test_user",
    )
    assert str(job) == "test_job (active)"
    assert repr(job) == (
        "Job(jobid=1, jobname='test_job', command='SELECT 1;', schedule='* * * * *', "
        "active=True, nodename='localhost', nodeport=5432, database='test_db', "
        "username='test_user')"
    )

    # When no jobname is provided, the jobid is used.
    job.jobname = None
    assert str(job) == "Job 1 (active)"
    assert repr(job) == (
        "Job(jobid=1, jobname=None, command='SELECT 1;', schedule='* * * * *', active=True, "
        "nodename='localhost', nodeport=5432, database='test_db', username='test_user')"
    )


def test_job_run_details_dunders() -> None:
    """Test the custom dunders for JobRunDetails."""
    start_time = dt.datetime.now(dt.timezone.utc)
    end_time = start_time + dt.timedelta(seconds=3600)
    job_run_details = JobRunDetails(
        runid=1,
        jobid=1,
        job_pid=1234,
        database="test_db",
        username="test_user",
        command="SELECT 1;",
        status="success",
        return_message="Completed",
        start_time=start_time,
        end_time=end_time,
    )
    assert str(job_run_details) == "Job 1 (success)"
    assert repr(job_run_details) == (
        "JobRunDetails(runid=1, jobid=1, job_pid=1234, database='test_db', "
        "username='test_user', command='SELECT 1;', status='success', "
        f"return_message='Completed', start_time={start_time!r}, end_time={end_time!r})"
    )


def test_job_run_details_duration() -> None:
    """Test the duration property of JobRunDetails."""
    start_time = dt.datetime.now(dt.timezone.utc)
    end_time = start_time + dt.timedelta(seconds=3600)
    job_run_details = JobRunDetails(
        runid=1,
        jobid=1,
        job_pid=1234,
        database="test_db",
        username="test_user",
        command="SELECT 1;",
        status="success",
        return_message="Completed",
        start_time=start_time,
        end_time=end_time,
    )
    assert job_run_details.duration == 3600.0
