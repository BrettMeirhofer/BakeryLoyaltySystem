from django.core.management.base import BaseCommand, CommandError
from Bakery import bulk_insert
from Bakery import models


class Command(BaseCommand):
    help = 'Imports the test data into the database'

    def handle(self, *args, **options):
        bulk_insert.bulk_import_with_dependencies([models.OrderLine, models.OrderReward, models.PointLog])
        self.stdout.write(self.style.SUCCESS("Successfully imported data"))