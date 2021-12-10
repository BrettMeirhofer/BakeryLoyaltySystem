from collections import defaultdict
from django.apps import apps
import csv
from os import path
from django.db import models

class BulkCreateManager(object):
    """
    This helper class keeps track of ORM objects to be created for multiple
    model classes, and automatically creates those objects with `bulk_create`
    when the number of objects accumulated for a given model class exceeds
    `chunk_size`.
    Upon completion of the loop that's `add()`ing objects, the developer must
    call `done()` to ensure the final set of objects is created for all models.
    """

    def __init__(self, chunk_size=100):
        self._create_queues = defaultdict(list)
        self.chunk_size = chunk_size

    def _commit(self, model_class):
        model_key = model_class._meta.label
        model_class.objects.bulk_create(self._create_queues[model_key])
        self._create_queues[model_key] = []

    def add(self, obj):
        """
        Add an object to the queue to be created, and call bulk_create if we
        have enough objs.
        """
        model_class = type(obj)
        model_key = model_class._meta.label
        self._create_queues[model_key].append(obj)
        if len(self._create_queues[model_key]) >= self.chunk_size:
            self._commit(model_class)

    def done(self):
        """
        Always call this upon completion to make sure the final partial chunk
        is saved.
        """
        for model_name, objs in self._create_queues.items():
            if len(objs) > 0:
                self._commit(apps.get_model(model_name))


def bulk_import_from_tsv(model_class):
    class_name = model_class.__name__
    file_path = path.join(path.dirname(path.dirname(path.dirname(__file__))), "TestData", class_name + "List.tsv")
    with open(file_path, 'r') as csv_file:
        bulk_mgr = BulkCreateManager(chunk_size=20)
        for row in csv.DictReader(csv_file, delimiter="\t"):
            bulk_mgr.add(model_class(**row))
        bulk_mgr.done()


def model_tree_to_list(model_class, model_list):
    model_object = model_class()
    model_fields = model_object._meta.get_fields(include_parents=False)
    for field in model_fields:
        if isinstance(field, models.ForeignKey):
            target_model = field.remote_field.model
            if target_model in model_list:
                continue
            else:
                model_list[target_model.__name__] = target_model
                model_tree_to_list(target_model, model_list)

    return list(model_list.values())


