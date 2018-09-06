from django.test import TestCase
from unittest.mock import MagicMock, patch
from management_scheduler.management.commands.scheduler import Command


class BaseTestCase(TestCase):
    def setUp(self):
        self.command = Command()
        self.command.scheduler = MagicMock()

    @patch('signal.signal')
    @patch('atexit.register')
    def test_management_command_configures_scheduler(self, signal, register):
        self.command.handle()
        self.assertTrue(self.command.scheduler.start.called)
        self.assertTrue(signal.called)
        self.assertTrue(register.called)
