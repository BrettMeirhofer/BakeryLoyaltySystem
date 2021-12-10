from django.test import TestCase
from Bakery import models
from bulk_insert import bulk_import_from_tsv, model_tree_to_list
from decimal import Decimal


class LookupModelTestCase(TestCase):
    model_class = models.ProductType
    rows = 19

    # 1st value is model id, 2nd is field name, 3rd is expected value
    assert_values = [[1, "product_type_name", "Breads"],
                     [19, "product_type_name", "Pies and Quiches"]]

    # Imports data for the model class and any models that it relies on
    def setUp(self):
        dependency_models = model_tree_to_list(self.model_class, {})
        for target_model in dependency_models:
            bulk_import_from_tsv(target_model)
        bulk_import_from_tsv(self.model_class)

    # Checking the number of rows catches issues with partial/failed imports
    def test_rows(self):
        self.assertEqual(self.model_class.objects.count(), self.rows)

    # Sampling parts of the data and comparing it known values helps to identify accidental transformations
    def test_values(self):
        for test_options in self.assert_values:
            self.assertEqual(getattr(self.model_class.objects.get(id=test_options[0]), test_options[1]), test_options[2])


# Testing status models is identical so the values are reused
class StoreStatusTestCase(LookupModelTestCase):
    model_class = models.StoreStatus
    rows = 2
    assert_values = [[1, "status_name", "Active"],
                     [2, "status_name", "Inactive"]]


class ProductStatusTestCase(StoreStatusTestCase):
    model_class = models.ProductStatus


class CustomerStatusTestCase(StoreStatusTestCase):
    rows = 3
    model_class = models.CustomerStatus


class BanTypeTestCase(StoreStatusTestCase):
    model_class = models.BanType
    assert_values = [[1, "ban_name", "Expensive"],
                     [2, "ban_name", "Custom"]]


class ProductTestCase(LookupModelTestCase):
    model_class = models.Product
    rows = 276
    assert_values = [[100, "product_price", Decimal("2.9900")],
                     [273, "product_type_id", 7],
                     [375, "product_status_id", 1],
                     [375, "product_name", "Siracha Chicken Pie"]]


class StoreTestCase(LookupModelTestCase):
    model_class = models.Store
    rows = 3
    assert_values = [[1, "store_name", "Store 1"],
                     [3, "store_status_id", 2]]


class PointReasonCase(LookupModelTestCase):
    model_class = models.PointReason
    rows = 2
    assert_values = [[1, "reason_name", "Complimentary  Points"],
                     [2, "reason_name", "System Failure"]]


#
class ModelTreeToListTestCase(TestCase):
    def test_model_tree_to_list(self):
        model_list = [models.ProductType, models.ProductStatus, models.BanType]
        self.assertEqual(model_list, model_tree_to_list(models.Product, {}))


# Test submitting a PointLog
# Test submitting a PointLog with negative points
# Test submitting an order with no orderlines
# Test submitting an order with no rewards
# Test submitting an order with both orderlines and rewards
# Test submitting an order with rewards cost greater then customer points
# Test submitting an order with a reward discount greater then order total
# Test submitting an order with an inactive customer
# Test submitting an order with inactive products
# Test submitting an order with inactive rewards
# Test submitting an order with banned products
# Test submitting an order with orderlines with quantities of 0
# Test submitting an order with 20 orderlines
