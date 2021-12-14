import random
import datetime
import os
import pandas
import names
import math
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


# Gets the path for a specific file in the data directory
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
    stores = stores.sample(num_customers, replace=True)
    customers = pandas.DataFrame()
    customers["store_id"] = stores["id"]
    store_dates = stores["start_date"].tolist()
    customers["begin_date"] = generate_dates_in_range(store_dates, end_date)
    customers.reset_index(drop=True, inplace=True)
    customers["id"] = customers.index + 1
    profile_header = ["first_name", "last_name", "email_address", "birthdate", "customer_status_id"]
    customers[profile_header] = generate_customer_profile(num_customers)
    customers["phone_number"] = generate_phones(input_dir, num_customers)
    customers_output = customers.drop(columns=["store_id"])
    path_name = data_path(output_dir, "CustomerList.tsv")
    customers_output.to_csv(path_name, index=False, sep="\t")

    orders = pandas.DataFrame()
    orders[["order_date", "store_id", "customer_id"]] = customers[["begin_date", "store_id", "id"]]
    orders = generate_additional_orders(orders, 200, end_date)
    set_df_id(orders)
    path_name = data_path(output_dir, "OrderList.tsv")
    orders.to_csv(path_name, index=False, sep="\t")

    reward_list = get_reward_list(output_dir)
    orders = orders.loc[orders["id"] > num_customers]
    orders = orders.sample(50)
    stores = orders["store_id"].tolist()
    order_rewards = []
    for store in stores:
        target_rewards = select_store_rewards(store, 1, reward_list)
        order_reward = target_rewards[0]
        order_rewards.append(order_reward)
    order_rewards = pandas.DataFrame(order_rewards)
    order_rewards.columns = ["reward_id", "point_cost", "free_product_id"]

    # If the tolist() is removed pandas deletes 90% of the values and converts the column to float
    order_rewards["order_id"] = orders["id"].tolist()
    set_df_id(order_rewards)
    path_name = data_path(output_dir, "OrderRewardList.tsv")
    order_rewards.to_csv(path_name, index=False, sep="\t")


# Generates additional Orders based on the order_date of the original Orders
def generate_additional_orders(orders, order_num, end_date):
    additional_orders = orders.sample(order_num, replace=True)
    original_dates = additional_orders["order_date"].tolist()
    dates = []
    for org_date in original_dates:
        new_date = date_in_range(org_date, end_date)
        dates.append(new_date)
    additional_orders["order_date"] = dates
    orders = orders.append(additional_orders)
    return orders


# Generates rewards based on the list of products
# This function is too big and should be split into more functions
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


# Merges ProductList and StoreProductList to produce a
# Dataframe that has both price and store data on each row
# So products can selected by store
def get_product_list(input_dir, output_dir):
    path_name = data_path(input_dir, "ProductList.tsv")
    ava_products = pandas.read_csv(path_name, delimiter="\t",
                                   converters={'product_price': lambda a: Decimal(a)})
    path_name = data_path(output_dir, "StoreProductList.tsv")
    store_products = pandas.read_csv(path_name, delimiter="\t")
    product_list = pandas.merge(ava_products, store_products, left_on="id", right_on="product_id", how="inner")
    return product_list


# Samples product data based on store and returns in list of list form
# Used to generate OrderLine information for a specific store
def select_store_products(store, num, product_list):
    product_list = product_list.loc[product_list["store_id"] == store]
    product_list = product_list.sample(num)
    product_list = product_list[["product_id", "product_price"]].values.tolist()
    return product_list


def get_reward_list(output_dir):
    path_name = data_path(output_dir, "RewardList.tsv")
    rewards = pandas.read_csv(path_name, delimiter="\t")
    path_name = data_path(output_dir, "StoreRewardList.tsv")
    store_rewards = pandas.read_csv(path_name, delimiter="\t")
    reward_list = pandas.merge(rewards, store_rewards, left_on="id", right_on="reward_id", how="inner")
    return reward_list


def select_store_rewards(store, num, reward_list):
    rewards = reward_list.loc[reward_list["store_id"] == store]
    rewards = rewards.sample(num)
    rewards = rewards[["reward_id", "point_cost", "free_product_id"]].values.tolist()
    return rewards


# Generates a random number of OrderLines for each Order
# The products available to the store of each Order is respected
# This function should be targeted first for optimization as it products the largest number of rows
def generate_order_lines(input_dir, output_dir, max_lines, max_qty):
    path_name = data_path(output_dir, "OrderList.tsv")
    orders = pandas.read_csv(path_name, delimiter="\t")
    product_list = get_product_list(input_dir, output_dir)
    stores = orders["store_id"].tolist()

    order_lines = []
    for order_index, store in enumerate(stores):
        num = random.randrange(1, max_lines + 1)
        selected_products = select_store_products(store, num, product_list)
        for index in range(num):
            order_line = [order_index+1]
            order_line.extend(selected_products[index-1])
            qty = random.randrange(1, max_qty + 1)
            order_line.append(qty)
            order_lines.append(order_line)
    order_lines = pandas.DataFrame(order_lines)
    order_lines.columns = ["order_id", "product_id", "ind_price", "quantity"]
    set_df_id(order_lines)
    path_name = data_path(output_dir, "OrderLineList.tsv")
    order_lines.to_csv(path_name, index=False, sep="\t")


# Creates a correctly ordered id column based on the dataframe index
def set_df_id(target_frame):
    target_frame.reset_index(inplace=True, drop=True)
    target_frame["id"] = target_frame.index + 1


# Generates PointLogs by randomly selecting customers
def generate_point_logs(input_dir, output_dir, log_num):
    path_name = data_path(output_dir, "CustomerList.tsv")
    customers = pandas.read_csv(path_name, delimiter="\t")
    point_logs = customers.sample(log_num)[["id", "begin_date"]]
    points = [random.randrange(1, 11) for x in range(log_num)]
    reason = [random.randrange(1, 3) for x in range(log_num)]
    point_logs["reason_id"] = reason
    point_logs["points_amount"] = points
    point_logs["customer_id"] = point_logs["id"]
    point_logs["created_date"] = point_logs["begin_date"]
    set_df_id(point_logs)
    point_logs = point_logs[["id", "created_date", "points_amount", "customer_id", "reason_id"]]
    path_name = data_path(output_dir, "PointLogList.tsv")
    point_logs.to_csv(path_name, index=False, sep="\t")


# Runs all the data generator functions in the correct order
def generate_data():
    input_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "TestData")
    output_dir = input_dir
    end_date = datetime.date(2021, 12, 12)
    generate_store_products(input_dir, output_dir)
    generate_customers(input_dir, output_dir, end_date)
    generate_rewards(input_dir, output_dir, 100)
    generate_order_lines(input_dir, output_dir, 5, 10)
    generate_point_logs(input_dir, output_dir, 50)

    #product_list = get_product_list(input_dir, output_dir)
    #store_products = select_store_products(2, 5, product_list)
    #print(store_products)


if __name__ == '__main__':
    generate_data()