"""Configuration options for `pgcron`."""

from __future__ import annotations

from django import db
from django.conf import settings


def get_database() -> str:
    """
    The database which `pgcron` is installed for,
    will be used as the default database for jobs.
    """
    database = getattr(settings, "PGCRON_DATABASE", db.DEFAULT_DB_ALIAS)
    if not isinstance(database, str):
        raise TypeError("PGCRON_DATABASE must be a string.")
    return database
