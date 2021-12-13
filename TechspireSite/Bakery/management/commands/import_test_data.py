from django.core.management.base import BaseCommand, CommandError
from Bakery import bulk_insert
from Bakery.models import Customer, StoreProduct


class Command(BaseCommand):
    help = 'Imports the test data into the database'

    def handle(self, *args, **options):
        bulk_insert.bulk_import_with_dependencies([Customer, StoreProduct])
        self.stdout.write(self.style.SUCCESS("Successfully imported data"))