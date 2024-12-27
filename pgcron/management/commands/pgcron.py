from __future__ import annotations

from typing import Any

from django.core.management import base as base_management

from pgcron import _jobs, _registry


class SubCommands(base_management.BaseCommand):  # pragma: no cover
    """
    Subcommand class vendored in from https://github.com/andrewp-as-is/django-subcommands.py.
    """

    argv: list[str] = []
    subcommands: dict[str, type[base_management.BaseCommand]] = {}

    def add_arguments(self, parser: base_management.CommandParser) -> None:
        subparsers = parser.add_subparsers(dest="subcommand", title="subcommands", description="")
        subparsers.required = True

        for command_name, command_class in self.subcommands.items():
            command = command_class()

            subparser = subparsers.add_parser(command_name, help=command_class.help)
            command.add_arguments(subparser)
            prog_name = subcommand = ""
            if self.argv:
                prog_name = self.argv[0]
                subcommand = self.argv[1]

            command_parser = command.create_parser(prog_name, subcommand)
            subparser._actions = command_parser._actions

    def run_from_argv(self, argv: list[str]) -> None:
        self.argv = argv
        return super().run_from_argv(argv)

    def handle(self, *args: Any, **options: Any) -> None:
        command_name = options["subcommand"]
        self.subcommands.get(command_name)
        command_class = self.subcommands[command_name]

        if self.argv:
            return command_class().run_from_argv([self.argv[0]] + self.argv[2:])
        else:
            return command_class().execute(*args, **options)


class LsCommand(base_management.BaseCommand):
    help = "List installed pgcron jobs."

    def handle(self, *args: Any, **options: Any) -> None:
        jobs = _jobs.all()
        registered_jobs = set(_registry.all())

        status_formatted = {
            _jobs.Status.ENABLED: "\033[92mENABLED\033[0m",
            _jobs.Status.DISABLED: "\033[91mDISABLED\033[0m",
        }

        if jobs != registered_jobs:
            self.stdout.write("Jobs are out of sync. Run `pgcron sync` to sync them.")

        if not jobs:
            self.stdout.write("No jobs found.")
            return

        max_status_len = max(len(status_formatted[job.status]) for job in jobs)
        for job in jobs:
            status = status_formatted[job.status]
            self.stdout.write(
                f"{{: <{max_status_len}}} {{}}".format(status, f"{job.uri} ({job.schedule})")
            )


class SyncCommand(base_management.BaseCommand):
    help = "Sync pgcron jobs with the database."

    def handle(self, *args: Any, **options: Any) -> None:
        jobs = _jobs.all()
        registered_jobs = set(_registry.all())
        jobs_to_register = registered_jobs - jobs
        jobs_to_drop = jobs - registered_jobs
        for job in jobs_to_drop:
            self.stdout.write(f"Dropping {job.name}...")
            job.drop()

        for job in jobs_to_register:
            self.stdout.write(f"Scheduling {job.name}...")
            job.register()


class UnscheduleCommand(base_management.BaseCommand):
    help = "Unschedule a pgcron job."

    def add_arguments(self, parser: base_management.CommandParser) -> None:
        parser.add_argument("name", help="The name of the job to unschedule.")

    def handle(self, *args: Any, **options: Any) -> None:
        name = options["name"]
        _jobs.unschedule(name)
        self.stdout.write(f"\033[91mUnscheduled {name}.\033[0m")


class EnableCommand(base_management.BaseCommand):
    help = "Enable a pgcron job."

    def add_arguments(self, parser: base_management.CommandParser) -> None:
        parser.add_argument("name", help="The name of the job to enable.")

    def handle(self, *args: Any, **options: Any) -> None:
        name = options["name"]
        _jobs.enable(name)
        self.stdout.write(f"\033[92mEnabled {name}.\033[0m")


class DisableCommand(base_management.BaseCommand):
    help = "Disable a pgcron job."

    def add_arguments(self, parser: base_management.CommandParser) -> None:
        parser.add_argument("name", help="The name of the job to disable.")

    def handle(self, *args: Any, **options: Any) -> None:
        name = options["name"]
        _jobs.disable(name)
        self.stdout.write(f"\033[91mDisabled {name}.\033[0m")


class Command(SubCommands):
    help = "Core django-pgcron subcommands."

    subcommands = {
        "ls": LsCommand,
        "sync": SyncCommand,
        "unschedule": UnscheduleCommand,
        "enable": EnableCommand,
        "disable": DisableCommand,
    }
