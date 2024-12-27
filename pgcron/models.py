"""Models for pgcron."""

from __future__ import annotations

from django.db import connections, models, transaction


class JobRunDetails(models.Model):
    """Pass-through model for `job_run_details`."""

    runid = models.BigAutoField(primary_key=True)
    jobid = models.BigIntegerField(db_index=True)
    job_pid = models.IntegerField()
    database = models.TextField()
    username = models.TextField()
    command = models.TextField()
    status = models.TextField()
    return_message = models.TextField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    class Meta:
        db_table = '"cron"."job_run_details"'
        managed = False

    @property
    def duration(self) -> float:
        return (self.end_time - self.start_time).total_seconds()

    def __str__(self) -> str:
        return f"Job {self.jobid} ({self.status})"

    def __repr__(self) -> str:
        return (
            f"JobRunDetails(runid={self.runid!r}, jobid={self.jobid!r}, job_pid={self.job_pid!r}, "
            f"database={self.database!r}, username={self.username!r}, command={self.command!r}, "
            f"status={self.status!r}, return_message={self.return_message!r}, "
            f"start_time={self.start_time!r}, end_time={self.end_time!r})"
        )


class JobQuerySet(models.QuerySet["Job"]):
    def unschedule(self) -> None:
        """Unschedule all jobs in the queryset.

        Note: It's not possible to unschedule jobs in a single query,
        so this incurs an O(jobs) cost.
        """
        with transaction.atomic(), connections[self.db].cursor() as cursor:
            for job in self:
                cursor.execute("SELECT cron.unschedule(%s);", [job.jobid])

    def enable(self) -> None:
        """Enable all jobs in the queryset."""
        self.update(active=True)

    def disable(self) -> None:
        """Disable all jobs in the queryset."""
        self.update(active=False)


class Job(models.Model):
    """Pass-through model for `jobs`."""

    jobid = models.BigAutoField(primary_key=True)
    schedule = models.TextField()
    command = models.TextField()
    # Defaults to `localhost`
    nodename = models.TextField()
    # Defaults to the server port.
    nodeport = models.IntegerField()
    # Defaults to the current database
    database = models.TextField()
    # Defaults to the current user
    username = models.TextField()
    # Whether the job is enabled.
    active = models.BooleanField()
    # Name for the job.
    jobname = models.TextField(null=True)

    objects: JobQuerySet = JobQuerySet.as_manager()  # type: ignore

    class Meta:
        db_table = '"cron"."job"'
        managed = False

    def __str__(self) -> str:
        name = self.jobname or f"Job {self.jobid}"
        status = "active" if self.active else "inactive"
        return f"{name} ({status})"

    def __repr__(self) -> str:
        return (
            f"Job(jobid={self.jobid!r}, jobname={self.jobname!r}, "
            f"command={self.command!r}, schedule={self.schedule!r}, "
            f"active={self.active!r}, nodename={self.nodename!r}, "
            f"nodeport={self.nodeport!r}, database={self.database!r}, "
            f"username={self.username!r})"
        )
