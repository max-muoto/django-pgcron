from __future__ import annotations

import dj_database_url

SECRET_KEY = "django-pgcron"
# Install the tests as an app so that we can make test models
INSTALLED_APPS = [
    "pgcron",
    "pgcron.tests",
]
DATABASES = {"default": dj_database_url.config()}

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

USE_TZ = False
