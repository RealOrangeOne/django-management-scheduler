from django.core.management.base import BaseCommand


class Command(BaseCommand):

    help = "no-op management command to assist testing django-management-scheduler"

    def handle(self, **options):
        pass
