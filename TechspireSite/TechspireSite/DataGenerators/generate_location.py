import csv
import pandas
import numpy as np
from faker import Faker
import os

if __name__ == '__main__':
    fake = Faker()
    addresses = []
    for index in range(0, 200):
        address = fake.address().split("\n")[0]
        addresses.append(address)
    zip_codes = pandas.read_csv("CityZip.tsv", sep="\t", header=None)
    cities = pandas.read_csv("City.tsv", sep="\t", header=None, index_col=0)
    zip_codes = zip_codes.sample(200)
    zip_codes = zip_codes[[0, 1]]
    zip_codes = zip_codes.join(cities, on=1, how="inner", lsuffix="l", rsuffix="r")
    zip_codes["addr"] = addresses
    zip_codes["state"] = 1407
    zip_codes = zip_codes.reset_index()
    zip_codes.index += 1
    zip_codes = zip_codes[[0, "1r", "addr", "state"]]
    zip_codes.loc[201] = ["77036", "Houston", "5700a Hillcroft Ave", 1407]
    zip_codes.loc[202] = ["77478", "Sugarland", "14025 Southwest Fwy #501", 1407]
    module_dir = os.path.dirname(__file__)
    path_name = os.path.join(os.path.dirname(module_dir), "SQL", "Data", "LocationList.tsv")
    zip_codes.to_csv(path_name, sep='\t', index=True, header=False)

#id,zip,city, address, state