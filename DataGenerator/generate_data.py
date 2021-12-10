import random
import datetime
import os
import pandas


def date_in_range(start_date, end_date):
    time_between_dates = end_date - start_date
    days_between_dates = time_between_dates.days + 1
    random_number_of_days = random.randrange(days_between_dates)
    random_date = start_date + datetime.timedelta(days=random_number_of_days)
    return random_date


#Builds the sql data directory string
def build_path():
    module_dir = os.path.dirname(__file__)
    base_path = os.path.join(os.path.dirname(module_dir), "SQL", "Data")
    return base_path


#Gets the path for a specific file in the sql data directory
def data_path(file_dir, file):
    return os.path.join(file_dir, file)


def generate_store_products(input_dir, output_dir):
    path_name = data_path(input_dir, "ProductList.tsv")
    products = pandas.read_csv(path_name, delimiter="\t")
    product_ids = products["ID"].values.tolist()
    path_name = data_path(input_dir, "StoreList.tsv")
    stores = pandas.read_csv(path_name, delimiter="\t", header=None)
    store_num = len(stores.index)
    store_dates = stores[5].tolist()
    store_products = []
    for target_product in product_ids:
        sample_num = random.randrange(1, store_num + 1)
        store_ids = stores[0].sample(sample_num).tolist()
        for store in store_ids:
            store_products.append([store_dates[store-1], target_product, store])
    store_products = pandas.DataFrame(store_products)
    store_products.index += 1
    path_name = data_path(output_dir, "StoreProductList.tsv")
    store_products.to_csv(path_name, header=False, index=True, sep="\t")




def generate_customers(input_dir, output_dir, num_customers=100):
    pass


def generate_data():
    input_dir = os.path.join(os.path.dirname(__file__), "Data", "Input")
    output_dir = os.path.join(os.path.dirname(__file__), "Data", "Output")


if __name__ == '__main__':
    generate_customers()