from __future__ import annotations

import dj_database_url

SECRET_KEY = "django-pgcron"
# Install the tests as an app so that we can make test models
INSTALLED_APPS = [
    "pgcron",
    "pgcron.tests",
]
DATABASES = {
    # The database where `pg_cron` PosgreSQL extension is installed in.
    # It can only be installed in one database. It's the one which has
    # `cron` schema. i.e. the default `PGCRON_DATABASE`
    "default": dj_database_url.config(),
    # pgcron jobs can be scheduled against a different database.
    "other": dj_database_url.config()
    | {"NAME": "other", "TEST": {"NAME": "other", "MIGRATE": False}},
}

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

USE_TZ = False
