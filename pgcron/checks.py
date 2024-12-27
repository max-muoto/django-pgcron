from __future__ import annotations

from typing import Any

from django.conf import settings
from django.core import checks


@checks.register(checks.Tags.compatibility)
def check_pgcron_installed(app_configs: Any, **kwargs: Any) -> list[checks.Error]:
    errors: list[checks.Error] = []

    if "pgcron" not in settings.INSTALLED_APPS:
        errors.append(
            checks.Error(
                'Add "pgcron" to settings.INSTALLED_APPS to use django-pgcron.',
                id="pgcron.E001",
            )
        )

    return errors
