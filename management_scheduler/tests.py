from unittest.mock import MagicMock, patch

from django.core.management import call_command
from django.test import TestCase

from management_scheduler.management.commands.scheduler import Command


@patch("signal.signal")
@patch("atexit.register")
@patch("functools.partial")
class SchedulerTestCase(TestCase):
    def setUp(self):
        self.command = Command()
        self.command.scheduler = MagicMock()

    def test_management_command_configures_scheduler(self, partial, signal, register):
        settings = {"noop": {"trigger": "interval", "minutes": 1}}
        with self.settings(MANAGEMENT_SCHEDULER=settings):
            self.command.handle()
        args, _ = partial.call_args_list[0]
        self.assertEqual(args[0], call_command)
        self.assertEqual(args[1], "noop")
        _, kwargs = self.command.scheduler.add_job.call_args_list[0]
        self.assertEqual(kwargs, settings["noop"])
