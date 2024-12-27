from __future__ import annotations

import pytest
from django.core import management

import pgcron
import pgcron._jobs
from pgcron import _registry
from pgcron.models import Job


@pytest.mark.django_db
def test_sync() -> None:
    """Test that the sync command works."""
    management.call_command("pgcron", "sync")
    assert Job.objects.count() == 0

    @pgcron.job(pgcron.crontab())
    def test_job():  # type: ignore
        return pgcron.SQLExpression("INSERT INTO name_model (name) VALUES ('test');")

    management.call_command("pgcron", "sync")
    assert Job.objects.count() == 1

    # Clean the registry (simulates a new sync with a new reload)
    _registry.clear()
    management.call_command("pgcron", "sync")
    assert Job.objects.count() == 0


@pytest.mark.django_db
def test_ls(capsys: pytest.CaptureFixture[str]) -> None:
    """Test that the ls command works."""
    management.call_command("pgcron", "ls")
    assert "No jobs found." in capsys.readouterr().out

    @pgcron.job(pgcron.crontab())
    def test_job():  # type: ignore
        return pgcron.SQLExpression("INSERT INTO name_model (name) VALUES ('test');")

    management.call_command("pgcron", "ls")
    assert "Jobs are out of sync. Run `pgcron sync` to sync them." in capsys.readouterr().out

    management.call_command("pgcron", "sync")
    management.call_command("pgcron", "ls")
    assert "test_job (* * * * *)" in capsys.readouterr().out


@pytest.mark.django_db
def test_enable_disable(capsys: pytest.CaptureFixture[str]) -> None:
    """Test that the enable command works."""

    @pgcron.job(pgcron.crontab())
    def test_job():  # type: ignore
        return pgcron.SQLExpression("INSERT INTO name_model (name) VALUES ('test');")

    management.call_command("pgcron", "sync")
    assert Job.objects.get().active is True

    management.call_command("pgcron", "disable", "pgcron.test_job")
    assert Job.objects.get().active is False
    assert "Disabled pgcron.test_job." in capsys.readouterr().out

    management.call_command("pgcron", "enable", "pgcron.test_job")
    assert Job.objects.get().active is True
    assert "Enabled pgcron.test_job." in capsys.readouterr().out


@pytest.mark.django_db
def test_unschedule(capsys: pytest.CaptureFixture[str]) -> None:
    """Test that the unschedule command works."""

    @pgcron.job(pgcron.crontab())
    def test_job():  # type: ignore
        return pgcron.SQLExpression("INSERT INTO name_model (name) VALUES ('test');")

    management.call_command("pgcron", "sync")
    assert Job.objects.count() == 1

    management.call_command("pgcron", "unschedule", "pgcron.test_job")
    assert Job.objects.count() == 0
    assert "Unscheduled pgcron.test_job." in capsys.readouterr().out
