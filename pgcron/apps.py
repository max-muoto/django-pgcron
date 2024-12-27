from __future__ import annotations

import importlib.util

from django.apps import AppConfig, apps


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
