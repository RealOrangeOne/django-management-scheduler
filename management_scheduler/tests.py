from unittest.mock import MagicMock, patch

from apscheduler.util import get_callable_name
from django.core.management import call_command
from django.test import TestCase

from management_scheduler.management.commands.scheduler import Command


def noop():
    pass


@patch("signal.signal")
@patch("atexit.register")
@patch("functools.partial")
class SchedulerTestCase(TestCase):
    def setUp(self):
        self.command = Command()
        self.command.scheduler = MagicMock()

    def test_management_command_configures_scheduler(self, partial, signal, register):
        settings = {"noop": ("interval", {"minutes": 10})}
        with self.settings(MANAGEMENT_SCHEDULER=settings):
            self.command.handle()
        args, _ = partial.call_args_list[0]
        self.assertEqual(args[0], call_command)
        self.assertEqual(args[1], "noop")
        args, kwargs = self.command.scheduler.add_job.call_args_list[0]
        self.assertEqual(kwargs, settings["noop"][1])
        self.assertEqual(args[1], settings["noop"][0])

    def test_supports_multiple_commands(self, partial, signal, register):
        settings = {
            "noop": ("interval", {"minutes": 10}),
            "scheduler": ("interval", {"minutes": 20}),
        }
        with self.settings(MANAGEMENT_SCHEDULER=settings):
            self.command.handle()
        self.assertEqual(len(self.command.scheduler.add_job.call_args_list), 2)
        self.assertEqual(len(partial.call_args_list), 2)
        self.assertListEqual(
            [job[0][1] for job in partial.call_args_list], ["noop", "scheduler"]
        )

    def test_validates_args(self, partial, signal, register):
        partial.return_value = noop
        settings = {"noop": ("interval", {"minutes": 10})}
        with self.settings(MANAGEMENT_SCHEDULER=settings):
            call_command("scheduler")

    def test_checks_valid_management_command(self, partial, signal, register):
        with self.settings(
            MANAGEMENT_SCHEDULER={"missing": ("interval", {"minutes": 10})}
        ):
            with self.assertRaises(LookupError) as e:
                call_command("scheduler")
        self.assertEqual(str(e.exception), "missing is not a valid management command")

    def test_checks_valid_trigger(self, partial, signal, register):
        with self.settings(MANAGEMENT_SCHEDULER={"noop": ("missing", {"minutes": 10})}):
            with self.assertRaises(LookupError) as e:
                call_command("scheduler")
        self.assertEqual(str(e.exception), 'No trigger by the name "missing" was found')

    def test_checks_valid_trigger_args(self, partial, signal, register):
        with self.settings(
            MANAGEMENT_SCHEDULER={"noop": ("interval", {"lightyears": 10})}
        ):
            with self.assertRaises(TypeError) as e:
                call_command("scheduler")
        self.assertEqual(
            str(e.exception),
            "__init__() got an unexpected keyword argument 'lightyears'",
        )

    def test_sets_job_name(self, partial, signal, register):
        with self.settings(
            MANAGEMENT_SCHEDULER={"noop": ("interval", {"minutes": 10})}
        ):
            self.command.handle()
        self.assertEqual(partial.call_args_list[0][0][1], "noop")
        self.assertEqual(
            get_callable_name(self.command.scheduler.add_job.call_args_list[0][0][0]),
            "noop",
        )
