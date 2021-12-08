import csv
import pandas
import os

def generate_state():
    raw_countries = pandas.read_csv("RawStates.csv")
    new = raw_countries[["id", "name", "country_id"]].copy()
    new.sort_values(by=['id'], inplace=True)
    module_dir = os.path.dirname(__file__)
    path_name = os.path.join(os.path.dirname(module_dir), "SQL", "Data", "StateProvinceList.tsv")
    new.to_csv(path_name, sep='\t', index=False, header=False)


if __name__ == '__main__':
    generate_state()


