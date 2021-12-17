from django.core.management.base import BaseCommand, CommandError
from Bakery import bulk_insert
from Bakery.models import *


# Imports test/demo data into the database and use sql to set the various calculated fields
class Command(BaseCommand):
    help = 'Imports the test data into the database'

    def handle(self, *args, **options):
        bulk_insert.bulk_import_bakery()
        bulk_insert.run_sql("CalculateOrderLineTotals.sql")
        bulk_insert.run_sql("CalculateOrderDetails.sql")
        bulk_insert.run_sql("CalculateCustomerPoints.sql")
        self.stdout.write(self.style.SUCCESS("Successfully imported data"))