from django.test import TestCase
from Bakery import models
import bulk_insert
from decimal import Decimal
from django.db.models import Max, Min


class LookupModelTestCase(TestCase):
    model_class = models.ProductType
    rows = 19

    # 1st value is model id, 2nd is field name, 3rd is expected value
    assert_values = [[1, "product_type_name", "Breads"],
                     [19, "product_type_name", "Pies and Quiches"]]

    # Imports data for the model class and any models that it relies on
    def setUp(self):
        bulk_insert.bulk_import_with_dependencies([self.model_class])

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


class ModelTreeToListTestCase(TestCase):
    # Tests that the output is in the same as expected in a 2-level tree
    def test_model_tree_to_list_product(self):
        model_list = [models.BanType, models.ProductStatus, models.ProductType]
        self.assertEqual(model_list, bulk_insert.model_tree_to_list([models.Product]))

    # Tests that the output is the same as expected in a 3-level tree
    def test_model_tree_to_list_store_product(self):
        model_list = [models.StoreStatus, models.Store, models.BanType,
                      models.ProductStatus, models.ProductType, models.Product]
        self.assertEqual(model_list, bulk_insert.model_tree_to_list([models.StoreProduct]))


class StoredSQLTestCase(TestCase):
    product_price_1 = Decimal("7.99")
    product_price_2 = Decimal("15.99")

    def setUp(self):
        bulk_insert.bulk_import_with_dependencies([models.OrderLine, models.OrderReward, models.PointLog])
        models.Product.objects.create(id=5001, product_price=self.product_price_1, product_name="Test1",
                                      product_type_id=1, product_status_id=1)
        models.StoreProduct.objects.create(id=5001, store_id=1, product_id=5001)

        models.Product.objects.create(id=5002, product_price=self.product_price_2, product_name="Test2",
                                      product_type_id=1, product_status_id=1, ban_reason_id=1)
        models.StoreProduct.objects.create(id=5002, store_id=1, product_id=5002)

    # Checks that OrderLine.save() correctly calculates and stores derived values
    def test_create_order_line(self):
        models.Order.objects.create(id=5001, customer_id=1, store_id=1)
        models.OrderLine.objects.create(id=5001, order_id=5001, product_id=5001, quantity=5)
        saved_order_line = models.OrderLine.objects.get(id=5001)
        self.assertTrue(Decimal("39.9500"), saved_order_line.total_price)
        self.assertTrue(saved_order_line.points_eligible)
        self.assertEqual(saved_order_line.ind_price, self.product_price_1)

    # Checks that the update script for importing OrderLines updates the totals correctly
    def test_calculate_order_line_totals(self):
        bulk_insert.run_sql("CalculateOrderLineTotals.sql")
        target_order_line = models.OrderLine.objects.get(id=1)
        expected_total = target_order_line.ind_price * target_order_line.quantity
        self.assertEqual(expected_total, target_order_line.total_price)

    # Checks that totals for the most basic order is calculated correctly
    def test_calculate_order_details(self):
        models.Order.objects.create(id=5005, customer_id=1, store_id=1)
        models.OrderLine.objects.create(id=5001, order_id=5005, product_id=5001, quantity=5)
        bulk_insert.run_sql("CalculateOrderDetails.sql")
        target_order = models.Order.objects.get(id=5005)
        expected_total = Decimal("39.9500")
        self.assertEqual(target_order.id, 5005)
        self.assertEqual(target_order.original_total, expected_total)
        self.assertEqual(target_order.final_total, expected_total)
        self.assertEqual(target_order.eligible_for_points, expected_total)
        self.assertEqual(target_order.points_produced, 3)
        self.assertEqual(target_order.points_total, 3)
        self.assertEqual(target_order.discount_amount, 0)


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
# Test submitting an order with orderlines that use the same product
# top_directory = path.dirname(path.dirname(path.dirname(__file__)))
# sql_path = path.join(top_directory, "SQL", "CalculateOrderLineTotals.sql")
