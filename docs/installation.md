
## Installation

Install `django-pgcron` with:


```bash
pip install django-pgcron
```

### Installing `pg_cron`

In order to use `django-pgcron`, you must have `pg_cron` installed in your database.

For instructions on installing `pg_cron`, see the [pg_cron documentation](https://github.com/citusdata/pg_cron?tab=readme-ov-file#installing-pg_cron). 

## Compatibility

`django-pgcron` is compatible with Python 3.11 - 3.15, Django 5.0+, and Postgres 13 - 18.
The minimum Postgres version also depends on Django: Django 5.2 and 6.0 require
Postgres 14+, while Django 6.1 requires Postgres 15+.
