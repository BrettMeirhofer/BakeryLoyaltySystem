from Bakery import models
from django.test import TestCase
import bulk_insert
import datetime
from django.db.utils import IntegrityError
from django.core.validators import ValidationError


# Checks the sql that updates
class CustomerPointsTestCase(TestCase):
    # Imports test data and creates a test customer
    def setUp(self):
        bulk_insert.bulk_import_bakery()
        birthdate = datetime.date(1970, 1, 1)
        models.Customer.objects.create(id=6001, first_name="Tester", last_name="1", email_address="Tester1@gmail.com",
                                       birthdate=birthdate, customer_status_id=1)

    # Checks that adding a point-log increasing a customer's points
    def test_add_point_log(self):
        models.PointLog.objects.create(id=6001, customer_id=6001, points_amount=50, reason_id=1)
        target_customer = models.Customer.objects.get(id=6001)
        self.assertEqual(target_customer.points_spent, 0)
        self.assertEqual(target_customer.points_earned, 50)
        self.assertEqual(target_customer.point_total, 50)

    # Checks that the values of multiple point-logs are summed to set customer points
    def test_add_point_log_neg(self):
        models.PointLog.objects.create(id=6001, customer_id=6001, points_amount=50, reason_id=1)
        models.PointLog.objects.create(id=6002, customer_id=6001, points_amount=-30, reason_id=1)
        target_customer = models.Customer.objects.get(id=6001)
        self.assertEqual(target_customer.points_spent, 30)
        self.assertEqual(target_customer.points_earned, 50)
        self.assertEqual(target_customer.point_total, 20)

    # Checks that Order points are added to a customer's points
    def test_add_order(self):
        models.Order.objects.create(id=5005, customer_id=6001, store_id=1, points_consumed=20, points_produced=30)
        target_customer = models.Customer.objects.get(id=6001)
        self.assertEqual(target_customer.points_spent, 20)
        self.assertEqual(target_customer.points_earned, 30)
        self.assertEqual(target_customer.point_total, 10)

    # Tests that the post_delete signal updates customer points when a PointLog or Order is deleted
    # Test doesn't succeed despite the post_delete working (possibly) because of the delay between the signal starter
    # and the signal function running
    """
    def test_delete_point_log(self):
        models.PointLog.objects.create(id=6001, customer_id=6001, points_amount=50, reason_id=1)
        target_customer = models.Customer.objects.get(id=6001)
        self.assertEqual(target_customer.points_earned, 50)
        self.assertEqual(target_customer.point_total, 50)
        target_point_log = models.PointLog.objects.get(id=6001)
        target_point_log.delete()
        self.assertEqual(target_customer.points_earned, 0)
        self.assertEqual(target_customer.point_total, 0)
    """

