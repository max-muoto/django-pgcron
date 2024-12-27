"""Manage pgcron schedules."""

from __future__ import annotations

from typing import Protocol, final


class Schedule(Protocol):
    """A schedule for a pgcron job."""

    def to_pgcron_expr(self) -> str:
        """Return the schedule as a pgcron expression."""
        raise NotImplementedError


@final
class crontab(Schedule):
    """A crontab for a pgcron job."""

    def __init__(
        self,
        minute: str = "*",
        hour: str = "*",
        day_of_month: str = "*",
        month_of_year: str = "*",
        day_of_week: str = "*",
    ) -> None:
        self.minute = minute
        self.hour = hour
        self.day_of_week = day_of_week
        self.day_of_month = day_of_month
        self.month_of_year = month_of_year

    def to_pgcron_expr(self) -> str:
        """Return the schedule as a pgcron expression."""
        return (
            f"{self.minute} {self.hour} {self.day_of_month} {self.month_of_year} {self.day_of_week}"
        )

    @classmethod
    def from_str(cls, expr: str) -> crontab:
        """Create a crontab from a string."""
        minute, hour, day_of_month, month_of_year, day_of_week = expr.split(" ")
        return cls(minute, hour, day_of_month, month_of_year, day_of_week)


@final
class seconds(Schedule):
    """Run a job every n seconds."""

    def __init__(self, n: int) -> None:
        if n < 1:
            raise ValueError("Interval must at least 1 second.")
        if n > 59:
            raise ValueError("Interval must be less than 60 seconds.")

        self.n = n

    def to_pgcron_expr(self) -> str:
        """Return the schedule as a pgcron expression."""
        return f"{self.n} seconds"
