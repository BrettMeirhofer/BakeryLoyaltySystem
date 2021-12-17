from Bakery import models
from django.test import TestCase
import bulk_insert
from decimal import Decimal


class LookupModelTestCase(TestCase):
    model_class = models.ProductType
    rows = 19

    # 1st value is model id, 2nd is field name, 3rd is expected value
    assert_values = [[1, "product_type_name", "Breads"],
                     [19, "product_type_name", "Pies and Quiches"]]

    # Imports data for the model class and any models that it relies on
    def setUp(self):
        bulk_insert.bulk_import_bakery()

    # Checking the number of rows catches issues with partial/failed imports
    def test_rows(self):
        self.assertEqual(self.model_class.objects.count(), self.rows)

    # Sampling parts of the data and comparing it known values helps to identify accidental transformations
    def test_values(self):
        for test_options in self.assert_values:
            self.assertEqual(getattr(self.model_class.objects.get(id=test_options[0]), test_options[1]),
                             test_options[2])


# Testing status models is identical so the values are reused
class StoreStatusTestCase(LookupModelTestCase):
    model_class = models.StoreStatus
    rows = 2
    assert_values = [[1, "status_name", "Active"],
                     [2, "status_name", "Inactive"]]


class ProductStatusTestCase(StoreStatusTestCase):
    model_class = models.ProductStatus


class RewardStatusTestCase(StoreStatusTestCase):
    model_class = models.RewardStatus


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
                     [3, "store_status_id", 1]]


class PointReasonTestCase(LookupModelTestCase):
    model_class = models.PointReason
    rows = 2
    assert_values = [[1, "reason_name", "Complimentary  Points"],
                     [2, "reason_name", "System Failure"]]


class StoreProductTestCase(LookupModelTestCase):
    model_class = models.StoreProduct
    rows = 276

    # The number of StoreProducts must be at-least equal to the number of Products
    def test_rows(self):
        self.assertTrue(self.model_class.objects.count() >= self.rows)

    # The data is generated so there are no reference values to use for test_values
    def test_values(self):
        pass


class CustomerTestCase(StoreProductTestCase):
    model_class = models.Customer
    rows = 100


class RewardTestCase(StoreProductTestCase):
    model_class = models.Reward
    rows = 30


class StoreRewardTestCase(StoreProductTestCase):
    model_class = models.StoreReward
    rows = 100


class OrderTestCase(StoreProductTestCase):
    model_class = models.Order
    rows = 100


class OrderLineTestCase(StoreProductTestCase):
    model_class = models.OrderLine
    rows = 100


class PointLogTestCase(StoreProductTestCase):
    model_class = models.PointLog
    rows = 50


class OrderRewardTestCase(StoreProductTestCase):
    model_class = models.OrderReward
    rows = 50