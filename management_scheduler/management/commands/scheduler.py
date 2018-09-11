import atexit
import functools
import logging
import signal

from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.schedulers.blocking import BlockingScheduler
from django.conf import settings
from django.core.management import call_command, get_commands
from django.core.management.base import BaseCommand

logger = logging.getLogger(__file__)


class Command(BaseCommand):

    scheduler = None

    def handle(self, **options):
        self.create_scheduler()
        self.configure_scheduler()
        self.setup_signals()
        self.start_scheduler()

    def create_scheduler(self):
        logger.info("Creating scheduler")
        self.scheduler = self.scheduler or BlockingScheduler(
            executors={"default": ThreadPoolExecutor(max_workers=4)}
        )

    def configure_scheduler(self):
        logger.info("Configuring scheduler")
        for command_name, (trigger, kwargs) in getattr(
            settings, "MANAGEMENT_SCHEDULER", {}
        ).items():
            if command_name not in get_commands():
                raise LookupError(
                    "{} is not a valid management command".format(command_name)
                )
            wrapped = functools.partial(call_command, command_name)
            wrapped.__qualname__ = command_name
            self.scheduler.add_job(wrapped, trigger, **kwargs)

    def start_scheduler(self):
        logger.info("Starting scheduler")
        if not settings.IN_TEST:
            self.scheduler.start()

    def setup_signals(self):
        signal.signal(signal.SIGINT, self.shutdown)
        signal.signal(signal.SIGTERM, self.shutdown)
        atexit.register(self.shutdown)

    def shutdown(self, *args, **kwargs):
        if self.scheduler.running:
            logger.info("Shutting down scheduler")
            self.scheduler.shutdown(wait=False)
