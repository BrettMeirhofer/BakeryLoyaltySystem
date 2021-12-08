import csv


def normalize_zip():
    cities = open('City.tsv', 'r', newline='')
    cities_reader = csv.reader(cities, delimiter='\t')

    city_zips = open('TexasZip.csv', 'r', newline='', )
    city_zips_reader = csv.reader(city_zips, delimiter=',')

    normal_city_zips = open('CityZip.tsv', 'w', newline='', )
    normal_city_zip_writer = csv.writer(normal_city_zips, delimiter="\t")

    city_list = {}
    for index, row in enumerate(cities_reader):
        city_list[row[1]] = index+1

    for row in city_zips_reader:
        try:
            index = city_list[row[1]]
            normal_city_zip_writer.writerow([row[0], index])
        except KeyError:
            pass






if __name__ == '__main__':
    normalize_zip()