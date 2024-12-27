# Usage

## Defining Jobs


### Executing SQL Expressions

The three primary ways of executing SQL expressions are:

1. `pgcron.SQLExpression` - A simple SQL expression to be executed by pgcron.
2. `pgcron.Update` - An update statement to be executed by pgcron.
3. `pgcron.Delete` - A delete statement to be executed by pgcron.



### `pgcron.SQLExpression`  

A `pgcron.SQLExpression` is a simple SQL expression to be executed by pgcron.

```python
import pgcron

@pgcron.job("0 0 1 1 *")
def my_job():
    return pgcron.SQLExpression("INSERT INTO my_table (name) VALUES ('test');")
```

### `pgcron.Update`

A `pgcron.Update` is an update statement to be executed by pgcron, with the ability to set values in the evaluated queryset.

```python
import pgcron

@pgcron.job("0 0 1 1 *")
def my_job():
    return pgcron.Update(NameTestModel.objects.all().filter(name="test"), name="test2")
```


### `pgcron.Delete`

A `pgcron.Delete` is a delete statement to be executed by pgcron.

```python
import pgcron

@pgcron.job("0 0 1 1 *")
def my_job():
    return pgcron.Delete(NameTestModel.objects.all().filter(name="test"))
```


!!! note

    Due to the immediate nature of `.update()` and `.delete()` you can not use them as return values for jobs, so you must use `pgcron.Update` and `pgcron.Delete` instead.


### Scheduling Jobs

Jobs are defined as functions decorated with `@pgcron.job`.  You can define the interval in two ways:

1. `pgcron.crontab` - A cron expression that defines the schedule.
2. `pgcron.seconds` - Runs the job every N seconds, ranging from 1 second to 59 seconds.


### `pgcron.crontab`

An example of a job that runs every minute, defined using a crontab expression:

```python
import pgcron

@pgcron.job("* * * * *")
def my_job():
    return pgcron.SQLExpression("INSERT INTO my_table (name) VALUES ('test');")
```

!!! note

    One thing to note about this crontab expression is that it is a cron expression that `$` is supported to indicate the last day of the month, something which isn't supported in all crontab implementations. You can create a cron schedule at [`crontab.guru`](https://crontab.guru/) to test your expression.


### `pgcron.seconds`

An example of a job that runs every 5 seconds:

```python
import pgcron

@pgcron.job("*/5 * * * *")
def my_job():
    return pgcron.SQLExpression("INSERT INTO my_table (name) VALUES ('test');")
```


!!! note

Right now, the only supported job type is `pgcron.SQLExpression`, which is a wrapper around a SQL string. Supporting ORM queries is difficult because of the fact that the typical actions you want to perform are not lazy (`delete()` , `update()` , etc).


### Custom Schedules

You also have the abilty to define custom schedule implementations, as long as it returns a value for `to_pgcron_expr()`.

```python
class Minutes:
    def __init__(self, minutes: int):
        self.minutes = minutes

    def to_pgcron_expr(self):
        return f"*/{self.minutes} * * * *"

@pgcron.job(Minutes(5))
def my_job():
    return pgcron.SQLExpression("INSERT INTO my_table (name) VALUES ('test');")
```

### Project Structure

Jobs should be defined in a `jobs.py` submodule within your Django app.


```
my_django_project/
│
├── my_app/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── jobs.py    <--- Add your jobs here
│   ├── migrations/
│   │   └── __init__.py
│   ├── models.py
│   ├── tests.py
│   ├── views.py
│   └── ...
```

## Syncing Jobs

After defining your jobs, sync them to the database using the `pgcron sync` command:

```bash
python manage.py pgcron sync
```

This command registers all current jobs and removes any jobs that are no longer defined in your application. It is recommended to run this command as part of your deployment process alongside `migrate`. 

!!! note

    Jobs created by `django-pgcron` have a custom prefix of `pgcron_v1__` to internally identify them and avoid conflicts with other jobs.

## Additional Commands

`django-pgcron` provides several management commands to manage your cron jobs:

- **List Jobs**: To list all installed pgcron jobs, use the `ls` command.
  
  ```bash
  python manage.py pgcron ls
  ```

- **Enable a Job**: To enable a specific job, use the `enable` command followed by the job name.
  
  ```bash
  python manage.py pgcron enable <job_name>
  ```

- **Disable a Job**: To disable a specific job, use the `disable` command followed by the job name.
  
  ```bash
  python manage.py pgcron disable <job_name>
  ```

- **Unschedule a Job**: To unschedule a specific job, use the `unschedule` command followed by the job name.
  
  ```bash
  python manage.py pgcron unschedule <job_name>
  ```
