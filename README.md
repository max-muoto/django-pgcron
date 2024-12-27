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

Defining your jobs is as simple as decorating a function returning with `@pgcron.job`. Three types of jobs are supported: `pgcron.Update`, `pgcron.Delete`, and `pgcron.SQLExpression`.


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

In order to use `django-pgcron`, you must have `pg_cron` installed in your database.

For instructions on installing `pg_cron`, see the [pg_cron documentation](https://github.com/citusdata/pg_cron?tab=readme-ov-file#installing-pg_cron). 


## Compatibility

`django-pgcron` is compatible with Python 3.10 - 3.13, Django 5.0+, and Postgres 13 - 17.

