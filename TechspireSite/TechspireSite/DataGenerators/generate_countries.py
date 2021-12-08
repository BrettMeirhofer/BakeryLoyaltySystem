import csv
import pandas
import os


def generate_countries():
    raw_countries = pandas.read_csv("RawCountries.csv")
    new = raw_countries[["id", "name"]].copy()
    module_dir = os.path.dirname(__file__)
    path_name = os.path.join(os.path.dirname(module_dir), "SQL", "Data", "CountryList.tsv")
    new.to_csv(path_name, sep='\t', index=False, header=False)


if __name__ == '__main__':
    generate_countries()

