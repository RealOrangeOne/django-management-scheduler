from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.executors.pool import ThreadPoolExecutor
from django.core.management.base import BaseCommand
from django.conf import settings
from django.core.management import call_command
import atexit
import logging
import signal
import functools


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
        self.scheduler = self.scheduler or BlockingScheduler(executors={'default': ThreadPoolExecutor(max_workers=4)})

    def configure_scheduler(self):
        logger.info("Configuring scheduler")
        for command_name, kwargs in getattr(settings, 'MANAGEMENT_SCHEDULER', {}).items():
            wrapped = functools.partial(call_command, command_name)
            wrapped.__qualname__ = command_name
            self.scheduler.add_job(wrapped, **kwargs)

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
