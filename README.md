# django-pgcron

`django-pgcron` is a Django library that enables you to manage scheduled cron jobs through Django's interface. It integrates with [`pg_cron`](https://github.com/citusdata/pg_cron), a Postgres extension that lets you schedule and automate database queries to run directly within PostgreSQL on a specified schedule, eliminating the need for Celery or another application-level job queuing library for simple database tasks.
 
## Quick Start

Install `django-pgcron` and add `pgcron` to your `INSTALLED_APPS` setting:

```python
INSTALLED_APPS = [
    ...
    "pgcron",
]
```

Jobs are intended to be scheduled in a `jobs.py` submodule of your app.


```
my_django_project/
│
├── my_app/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── jobs.py <--- Add your jobs here
│   ├── migrations/
│   │   └── __init__.py
│   ├── models.py
│   ├── tests.py
│   ├── views.py
│   └── ...
```

Defining your jobs is as simple as decorating a function returning with `@pgcron.job`. Three types of jobs are supported: `pgcron.Update`, `pgcron.Delete`, and `pgcron.SQLExpression`. The `database` argument selects which database the job runs in, see [Multiple databases](#multiple-databases).


### Update

A `pgcron.Update` is an update statement on an ORM query.

```python
import pgcron

@pgcron.job("0 0 1 1 *")
def my_job():
    return pgcron.Update(NameTestModel.objects.all().filter(name="test"), name="test2")
```

### Delete

A `pgcron.Delete` is a delete statement on an ORM query.

```python
import pgcron

@pgcron.job("0 0 1 1 *")
def my_job():
    return pgcron.Delete(NameTestModel.objects.all().filter(name="test"))
```

### SQL Expressions

A `pgcron.SQLExpression` is a simple SQL expression to be executed by pgcron.

```python
import pgcron

@pgcron.job("0 0 1 1 *")
def my_job():
    return pgcron.SQLExpression("INSERT INTO my_table (name) VALUES ('test');")
```

### Schedules

`@pgcron.job` takes a crontab expression as a string, or a `pgcron.seconds(n)` interval for jobs that run every n seconds (1-59).

Schedule expressions are passed to `pg_cron` as-is and validated by the server. See the [pg_cron documentation](https://github.com/citusdata/pg_cron#cron-syntax) for the supported syntax. Note that `pg_cron` >= 1.6.5 rejects step values larger than a field's maximum, for example `* * * * */10` is invalid because day of week is 0-7. This validation was added in pg_cron 1.6.5 while fixing the CVE-2024-43688 cron parser underflow (https://github.com/citusdata/pg_cron/issues/351).

### Syncing Jobs

Once you've defined your jobs, you can sync them to the database with the `pgcron sync` command.

```bash
python manage.py pgcron sync
```

This will register all of your current jobs, and drop any jobs that are no longer defined in your application. It's recommended to run this command as part of your application's deployment process alongside `migrate`.


## Installation

Install `django-pgcron` with:


```bash
pip install django-pgcron
```

### Installing `pg_cron`

In order to use `django-pgcron`, you must have `pg_cron` installed in the database it manages jobs from (by default, your default database; override with `PGCRON_DATABASE` in settings, see [Multiple databases](#multiple-databases)).

Note that `pg_cron` can only be installed in a single database per cluster, but jobs can still be scheduled to run against other databases.

For instructions on installing `pg_cron`, see the [pg_cron documentation](https://github.com/citusdata/pg_cron?tab=readme-ov-file#installing-pg_cron). 


## Multiple databases

By default, all jobs run in the database `pg_cron` is installed in. To run a job against a different database on the same server, pass the `database` argument to `pgcron.job`:

```python
import pgcron

@pgcron.job("0 0 * * *", database="analytics")
def nightly_vacuum():
    return pgcron.SQLExpression("VACUUM;")
```

`database` is a `DATABASES` alias. The target database must exist, and the user that schedules the job needs `CONNECT` privilege on it.

If `pg_cron` is installed in a database other than your default one, point `PGCRON_DATABASE` at it:

```python
# settings.py
DATABASES = {
    "default": {...},
    "pgcron": {...},  # the database where `CREATE EXTENSION pg_cron` was run
}
PGCRON_DATABASE = "pgcron"
```

The `cron` schema only exists in that database, so all job management (`pgcron sync`, `pgcron ls`, enabling, disabling, dropping) happens there, regardless of which database a job runs against. The `Job` and `JobRunDetails` models are pass-throughs for that database's tables; when querying them directly, use the alias explicitly:

```python
from django.conf import settings

pgcron.models.Job.objects.using(settings.PGCRON_DATABASE).filter(...)
```

## Compatibility

`django-pgcron` is compatible with Python 3.10 - 3.13, Django 5.0+, and Postgres 13 - 17.

