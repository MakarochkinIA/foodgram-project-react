from django.core.management.base import BaseCommand

from api.v1.utils import load_data


class Command(BaseCommand):
    def handle(self, *args, **options):
        load_data()
