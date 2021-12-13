import datetime
from DataGenerator import generate_data
from unittest import TestCase
import os


class DateInRangeTestCase(TestCase):
    # Tests that the output is between the start and end dates
    def test_date_in_range_different(self):
        start_date = datetime.date(2000, 11, 11)
        end_date = datetime.date(2021, 11, 18)
        output_date = generate_data.date_in_range(start_date, end_date)
        self.assertTrue(start_date <= output_date <= end_date)

    # Tests that the output will be the given start/end date if those dates are identical
    def test_date_in_range_same(self):
        start_date = datetime.date(2021, 11, 18)
        end_date = datetime.date(2021, 11, 18)
        self.assertEqual(generate_data.date_in_range(start_date, end_date), start_date)

    # Tests that a ValueError exception will be raised if the end_date is before the start_date
    def test_date_in_range_neg(self):
        start_date = datetime.date(2021, 11, 18)
        end_date = datetime.date(2021, 11, 17)
        with self.assertRaises(ValueError):
            generate_data.date_in_range(start_date, end_date)

    # Tests that the random includes the given start and end values as possible outputs
    def test_date_in_range_inclusion(self):
        start_date = datetime.date(2021, 11, 17)
        end_date = datetime.date(2021, 11, 18)
        generated_dates = [generate_data.date_in_range(start_date, end_date) for x in range(100)]
        self.assertTrue(start_date in generated_dates and end_date in generated_dates)


class DataGeneratorTestCase(TestCase):
    input_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "TestData")
    output_dir = os.path.join(os.path.dirname(__file__), "Data")
    end_date = datetime.date(2021, 12, 12)

    def test_generate_store_products(self):
        generate_data.generate_store_products(self.input_dir, self.output_dir)
        output_exists = os.path.exists(os.path.join(self.output_dir, "StoreProductList.tsv"))
        self.assertTrue(output_exists)

    def test_generate_customers(self):
        generate_data.generate_customers(self.input_dir, self.output_dir, self.end_date, 200)
        output_exists = os.path.exists(os.path.join(self.output_dir, "CustomerList.tsv"))
        self.assertTrue(output_exists)

    def test_generate_rewards(self):
        generate_data.generate_store_products(self.input_dir, self.output_dir)
        generate_data.generate_rewards(self.input_dir, self.output_dir, 100)
        rewards_exists = os.path.exists(os.path.join(self.output_dir, "RewardList.tsv"))
        store_rewards_exists = rewards_exists = os.path.exists(os.path.join(self.output_dir, "StoreRewardList.tsv"))
        self.assertTrue(rewards_exists and store_rewards_exists)





