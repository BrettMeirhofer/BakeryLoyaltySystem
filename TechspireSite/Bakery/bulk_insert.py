from collections import defaultdict
from django.apps import apps
import csv
from django.db import connection
from os import path
from Bakery import models



# Creates a path to the directory where raw SQL is stored
# Modify if the SQL directory is moved
def get_sql_text(file_name):
    top_directory = path.dirname(path.dirname(path.dirname(__file__)))
    sql_path = path.join(top_directory, "SQL", file_name)
    return open(sql_path).read()


# Packages running a single sql statement with no output against the database into a single function
def run_sql(file_name, sql_params=None):
    sql_text = get_sql_text(file_name)
    with connection.cursor() as cursor:
        if sql_params is None:
            cursor.execute(sql_text)
        else:
            cursor.execute(sql_text, sql_params)


# Chunks the creation of Django objects. Changing chunk_size allows optimization of memory usage vs database calls
class BulkCreateManager(object):
    def __init__(self, chunk_size=100):
        self._create_queues = defaultdict(list)
        self.chunk_size = chunk_size

    # Performs a bulk insert on all objects in the queue
    def _commit(self, model_class):
        model_key = model_class._meta.label
        model_class.objects.bulk_create(self._create_queues[model_key])
        self._create_queues[model_key] = []

    # Adds objects to the queue. Commits objects once the queue is full
    def add(self, obj):
        model_class = type(obj)
        model_key = model_class._meta.label
        self._create_queues[model_key].append(obj)
        if len(self._create_queues[model_key]) >= self.chunk_size:
            self._commit(model_class)

    # Call once done to create any remaining objects
    def done(self):
        for model_name, objs in self._create_queues.items():
            if len(objs) > 0:
                self._commit(apps.get_model(model_name))


# Given a model search for a file called ModelNameList.tsv to import to the database
# Each row is converted to a dict which is used to init a Model object
def bulk_import_from_tsv(model_class):
    class_name = model_class.__name__
    file_path = path.join(path.dirname(path.dirname(path.dirname(__file__))), "TestData", class_name + "List.tsv")
    with open(file_path, 'r') as csv_file:
        bulk_mgr = BulkCreateManager(chunk_size=20)
        for row in csv.DictReader(csv_file, delimiter="\t"):
            # Removes all empty strings from the row dict
            row = {k: v for k, v in row.items() if v != ""}
            bulk_mgr.add(model_class(**row))
        bulk_mgr.done()


def bulk_import_bakery():
    model_list = [models.CustomerStatus, models.RewardStatus, models.StoreStatus, models.BanType, models.PointReason, models.ProductType,
                  models.ProductStatus, models.Product, models.Customer, models.Store, models.Reward,
                  models.StoreReward, models.StoreProduct]
    for target_model in model_list:
        bulk_import_from_tsv(target_model)
