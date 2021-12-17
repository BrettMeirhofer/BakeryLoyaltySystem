from Bakery import models
from django.test import TestCase
import bulk_insert
from decimal import Decimal


class StoredSQLTestCase(TestCase):
    product_price_1 = Decimal("7.99")
    product_price_2 = Decimal("15.99")

    def setUp(self):
        bulk_insert.bulk_import_bakery()
        models.Product.objects.create(id=5001, product_price=self.product_price_1, product_name="Test1",
                                      product_type_id=1, product_status_id=1)
        models.StoreProduct.objects.create(id=5001, store_id=1, product_id=5001)

        models.Product.objects.create(id=5002, product_price=self.product_price_2, product_name="Test2",
                                      product_type_id=1, product_status_id=1, ban_reason_id=1)
        models.StoreProduct.objects.create(id=5002, store_id=1, product_id=5002)

        models.Reward.objects.create(id=5001, point_cost=10, reward_name="BaseReward", reward_status_id=1,
                                     free_product_id=5001)
        models.StoreReward.objects.create(id=5001, store_id=1, reward_id=5001)

        models.Reward.objects.create(id=5002, point_cost=15, reward_name="DiscountReward", reward_status_id=1,
                                     discount_amount=Decimal("5.0000"), free_product_id=5002)
        models.StoreReward.objects.create(id=5002, store_id=1, reward_id=5002)

    # Checks that OrderLine.save() correctly calculates and stores derived values
    def test_create_order_line(self):
        models.Order.objects.create(id=5001, customer_id=1, store_id=1)
        models.OrderLine.objects.create(id=5001, order_id=5001, product_id=5001, quantity=5)
        saved_order_line = models.OrderLine.objects.get(id=5001)
        self.assertTrue(Decimal("39.9500"), saved_order_line.total_price)
        self.assertTrue(saved_order_line.points_eligible)
        self.assertEqual(saved_order_line.ind_price, self.product_price_1)

    # Checks that OrderReward.save() correctly calculates and stores derived values
    def test_create_order_reward(self):
        models.Order.objects.create(id=5005, customer_id=1, store_id=1)
        models.OrderReward.objects.create(id=5001, order_id=5005, reward_id=5002)
        target_reward = models.OrderReward.objects.get(id=5001)
        self.assertEqual(target_reward.discount_amount, Decimal("5.0000"))
        self.assertEqual(target_reward.free_product_id, 5002)
        self.assertEqual(target_reward.point_cost, 15)

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
        self.assertEqual(target_order.original_total, expected_total)
        self.assertEqual(target_order.final_total, expected_total)
        self.assertEqual(target_order.eligible_for_points, expected_total)
        self.assertEqual(target_order.points_produced, 3)
        self.assertEqual(target_order.points_total, 3)

    # Checks that totals are correct when there are multiple orderlines and only some of them are eligible for points
    def test_calculate_order_details_multiple(self):
        models.Order.objects.create(id=5005, customer_id=1, store_id=1)
        models.OrderLine.objects.create(id=5001, order_id=5005, product_id=5001, quantity=8)
        models.OrderLine.objects.create(id=5002, order_id=5005, product_id=5002, quantity=2)
        bulk_insert.run_sql("CalculateOrderDetails.sql")
        target_order = models.Order.objects.get(id=5005)
        expected_total = Decimal("95.9000")
        self.assertEqual(target_order.original_total, expected_total)
        self.assertEqual(target_order.final_total, expected_total)
        self.assertEqual(target_order.eligible_for_points, Decimal("63.9200"))
        self.assertEqual(target_order.points_produced, 6)
        self.assertEqual(target_order.points_total, 6)

    # Checks that totals are correct when there is a reward that consumes points
    def test_calculate_order_details_point_cost(self):
        models.Order.objects.create(id=5005, customer_id=1, store_id=1)
        models.OrderLine.objects.create(id=5001, order_id=5005, product_id=5001, quantity=8)
        models.OrderReward.objects.create(id=5001, order_id=5005, reward_id=5001)
        bulk_insert.run_sql("CalculateOrderDetails.sql")
        target_order = models.Order.objects.get(id=5005)
        expected_total = Decimal("63.9200")
        self.assertEqual(target_order.original_total, expected_total)
        self.assertEqual(target_order.final_total, expected_total)
        self.assertEqual(target_order.eligible_for_points, expected_total)
        self.assertEqual(target_order.points_produced, 6)
        self.assertEqual(target_order.points_consumed, 10)
        self.assertEqual(target_order.points_total, -4)



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
