import random
import datetime
import os
import pandas
import names
from decimal import Decimal


# Generates a list of phone numbers given a list of area codes
def generate_phones(input_dir, count):
    country = "+1"
    path_name = data_path(input_dir, "TexasAreaCodes.tsv")
    area_codes = pandas.read_csv(path_name, sep="\t")
    area_codes = area_codes.sample(count, replace=True)
    codes = area_codes["code"].tolist()
    numbers = []
    for code in codes:
        last_digits = ""
        for index in range(0, 7):
            digit = random.randrange(0, 10)
            last_digits += str(digit)
        numbers.append(country + str(code) + last_digits)
    return numbers


# Generates an inclusive date in range given a start and end date
def date_in_range(start_date, end_date):
    time_between_dates = end_date - start_date
    days_between_dates = time_between_dates.days + 1
    random_number_of_days = random.randrange(days_between_dates)
    random_date = start_date + datetime.timedelta(days=random_number_of_days)
    return random_date


# Gets the path for a specific file in the sql data directory
def data_path(file_dir, file):
    return os.path.join(file_dir, file)


# Given a Store and Product dataframe creates a merged dataframe
# Assigning products to one or more stores
def store_products_random_join(stores, products):
    product_ids = products["id"].values.tolist()
    store_num = len(stores.index)
    store_dates = stores["start_date"].tolist()
    store_products = []
    for target_product in product_ids:
        sample_num = random.randrange(1, store_num + 1)
        store_ids = stores["id"].sample(sample_num).tolist()
        for store in store_ids:
            store_products.append([store_dates[store-1], target_product, store])
    store_products = pandas.DataFrame(store_products)
    return store_products


# Uses ProductList and StoreList to create StoreProductList.
# Because a product must be assigned to a store to be accessible to the Order system
def generate_store_products(input_dir, output_dir):
    path_name = data_path(input_dir, "ProductList.tsv")
    products = pandas.read_csv(path_name, delimiter="\t")
    path_name = data_path(input_dir, "StoreList.tsv")
    stores = pandas.read_csv(path_name, delimiter="\t")
    store_products = store_products_random_join(stores, products)
    store_products.columns = ["product_assigned", "product_id", "store_id"]
    store_products.index += 1
    path_name = data_path(output_dir, "StoreProductList.tsv")
    store_products.to_csv(path_name, index=False, sep="\t")


# Generates a list of dates using a list of start_dates and a single end_date
def generate_dates_in_range(start_dates, end_date):
    out_dates = []
    for start_date in start_dates:
        start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
        out_date = date_in_range(start_date, end_date)
        out_dates.append(out_date)
    return out_dates


# Generates a list of lists of basic profile data for a customer
def generate_customer_profile(num_customers, start_date=None, end_date=None):
    if start_date is None:
        start_date = datetime.date(1960, 1, 1)

    if end_date is None:
        end_date = datetime.date(1990, 1, 1)

    cust_info = []
    for index in range(num_customers):
        first_name = names.get_first_name()
        last_name = names.get_last_name()
        email = first_name + last_name + "@gmail.com"
        status = random.choice([1, 1, 1, 1, 1, 2, 2, 3])
        birth_date = date_in_range(start_date, end_date)
        cust_info.append([first_name, last_name, email, birth_date, status])
    return cust_info


# Generates CustomerList from StoreList
# Customers are needed to place Orders in the system
def generate_customers(input_dir, output_dir, end_date, num_customers=100):
    path_name = data_path(input_dir, "StoreList.tsv")
    stores = pandas.read_csv(path_name, delimiter="\t")
    store_dates = stores.sample(num_customers, replace=True)
    store_dates = store_dates["start_date"].tolist()
    customers = pandas.DataFrame()
    customers["begin_date"] = generate_dates_in_range(store_dates, end_date)
    customers["id"] = customers.index + 1
    profile_header = ["first_name", "last_name", "email_address", "birthdate", "customer_status_id"]
    customers[profile_header] = generate_customer_profile(num_customers)
    customers["phone_number"] = generate_phones(input_dir, num_customers)
    path_name = data_path(output_dir, "CustomerList.tsv")
    customers.to_csv(path_name, index=False, sep="\t")


#Generates rewards based on the list of products
def generate_rewards(input_dir, output_dir, num_rewards=100):
    max_product_price = 20
    default_status = 1

    #Inner joins Products and Store Products
    #Because columns values from both tables are needed to build a reward
    path_name = data_path(input_dir, "ProductList.tsv")
    products = pandas.read_csv(path_name, delimiter="\t", converters={'product_price': lambda a: Decimal(a)})
    path_name = data_path(output_dir, "StoreProductList.tsv")
    store_products = pandas.read_csv(path_name, delimiter="\t")
    products = pandas.merge(products, store_products, left_on="id", right_on="product_id", how="inner")

    #Samples products that cost less then $20 for use as reward templates
    #because the client doesn't want expensive items to be used for rewards
    products["point_cost"] = products["product_price"].astype(int)
    products = products.loc[products["point_cost"] <= max_product_price]
    rewards = products.sample(num_rewards)

    #Generates or assigns values to columns
    rewards["free_product_id"] = rewards["id"]
    rewards[["reset_period", "date_disabled", "reward_desc"]] = ""
    rewards["discount_amount"] = 0
    rewards["reward_status_id"] = default_status
    original_headers = ["product_assigned", "product_name", "product_desc"]
    new_headers = ["date_added", "reward_name", "reward_desc"]
    rewards[new_headers] = rewards[original_headers]

    #Fixes the index and removes unnecessary columns before saving to file
    rewards.reset_index(inplace=True)
    store_rewards = rewards[["id", "store_id", "date_added", "product_id"]].copy()
    rewards.drop_duplicates(subset=["product_id"], inplace=True)
    rewards.reset_index(inplace=True)
    rewards["id"] = rewards.index + 1
    rewards_output = rewards[["id", "reward_name", "reward_desc", "point_cost", "reset_period", "discount_amount",
                              "date_added", "date_disabled", "reward_status_id", "free_product_id"]]
    path_name = data_path(output_dir, "RewardList.tsv")
    rewards_output.to_csv(path_name, index=False, sep="\t")

    #Extracts the relevant fields for StoreRewards from the rewards dataframe then saves it to file
    store_rewards = pandas.merge(store_rewards, rewards[["id", "product_id"]], left_on="product_id", right_on="product_id", how="inner")
    store_rewards.reset_index(inplace=True, drop=True)
    store_rewards["id"] = store_rewards.index + 1
    store_rewards = store_rewards[["id", "store_id", "date_added", "id_y"]]
    path_name = data_path(output_dir, "StoreRewardList.tsv")
    store_rewards.to_csv(path_name, index=False, sep="\t", header=["id", "store_id", "reward_assigned", "reward_id"])


# Runs all the data generator functions in the correct order
def generate_data():
    input_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "TestData")
    output_dir = input_dir
    end_date = datetime.date(2021, 12, 12)
    generate_store_products(input_dir, output_dir)
    generate_customers(input_dir, output_dir, end_date)
    generate_rewards(input_dir, output_dir, 100)


if __name__ == '__main__':
    generate_data()