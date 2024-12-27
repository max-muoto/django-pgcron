from __future__ import annotations

import contextlib
import copy
from typing import TYPE_CHECKING, Any

import pytest
from django.core import management
from django.db import connection

from pgcron import _registry
from pgcron.models import JobRunDetails
from pgcron.tests.models import NameTestModel

if TYPE_CHECKING:
    from collections.abc import Generator


@contextlib.contextmanager
def add_other_database() -> Generator[None]:
    from django.conf import settings

    original_settings = copy.deepcopy(settings.DATABASES)
    try:
        settings.DATABASES["other"] = {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": "other",
            "USER": "postgres",
            "PASSWORD": "postgres",
            "HOST": "localhost",
            "PORT": 5432,
            "OPTIONS": {"pool": False},
            "TEST": {"NAME": "other", "MIRROR": "default", "MIGRATE": False},
        }
        yield
    finally:
        settings.DATABASES = original_settings


@pytest.fixture(scope="session", autouse=True)
def pgcron_extension(django_db_setup: Any, django_db_blocker: Any) -> Generator[None]:
    """Swtich out database to our instance pre-configured with pgcron."""
    with django_db_blocker.unblock(), connection.cursor():
        # Reconnect with new settings.
        connection.close()
        connection.settings_dict["NAME"] = "postgres"
        connection.settings_dict["TIME_ZONE"] = None
        connection.connect()
        yield


@pytest.fixture(autouse=True)
def clear_registry() -> None:
    """Clear the registry before each test to avoid state leakage."""
    _registry.clear()


@pytest.fixture(autouse=True)
def current_db(settings: Any) -> str:
    """Return the current database."""
    return settings.DATABASES["default"]["NAME"]


@pytest.fixture(autouse=True)
def reset_job_state() -> None:
    """Sync jobs to the database."""
    management.call_command("pgcron", "sync")
    JobRunDetails.objects.all().delete()
    NameTestModel.objects.all().delete()
