from __future__ import annotations

import importlib.util
from typing import Any

from django.apps import AppConfig, apps
from django.conf import settings
from django.core import management
from django.db.models.signals import post_migrate


def _sync_on_migrate_enabled() -> bool:
    """Sync pgcron jobs on migrate."""
    sync_on_migrate = getattr(settings, "PGCRON_SYNC_ON_MIGRATE", True)
    if not isinstance(sync_on_migrate, bool):
        raise TypeError("PGCRON_SYNC_ON_MIGRATE must be a boolean.")
    return sync_on_migrate


def _sync_on_migrate_receiver(**kwargs: Any) -> None:
    """Sync pgcron jobs on migrate."""
    management.call_command("pgcron", "sync")


def _discover_cron_jobs() -> None:
    """Discover and register pgcron jobs."""
    for app in apps.get_app_configs():
        if app.module is None:  # pragma: no cover - for type-checker
            continue

        jobs_module = f"{app.module.__name__}.jobs"
        module_spec = importlib.util.find_spec(jobs_module)
        if module_spec is not None:
            importlib.import_module(jobs_module)


class PGCronConfig(AppConfig):
    name = "pgcron"

    def ready(self) -> None:
        """Find all pgcron jobs and register them with django-pgcron."""
        _discover_cron_jobs()
        if _sync_on_migrate_enabled():
            post_migrate.connect(_sync_on_migrate_receiver)
