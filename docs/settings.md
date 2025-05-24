# Settings

Below are all settings for `django-pgcron`.

## `PGCRON_SYNC_ON_MIGRATE`

If `True`, `python3 manage.py pgcron sync` will automatically run after `python manage.py migrate`. This will install and register all of your defined cron jobs in the database, ensuring they are up-to-date after each migration. Default is `True`.

## `PGCRON_DATABASE`

The database where pg_cron jobs are installed. Defaults to Django's `DEFAULT_DB_ALIAS`.
