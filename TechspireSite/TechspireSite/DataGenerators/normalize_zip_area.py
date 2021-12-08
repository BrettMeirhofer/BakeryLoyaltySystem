import csv

#split area code csv into area, city, and area_city files
def normalize_zip_area():
    raw_area_codes = open('TexasAreaCodes.tsv', 'r', newline='', )
    raw_reader = csv.reader(raw_area_codes, delimiter='\t')

    city = open('City.tsv', 'w', newline='', )
    city_writer = csv.writer(city, delimiter="\t")

    area = open('Area.tsv', 'w', newline='', )
    area_writer = csv.writer(area, delimiter="\t")

    area_city = open('Area_City.tsv', 'w', newline='', )
    area_city_writer = csv.writer(area_city, delimiter="\t")

    city_count = 1
    area_count = 1

    for row in raw_reader:
        areas = row[0].split(",")
        cites = row[1].split(",")
        area_ids = []
        city_ids = []
        for area in areas:
            area_writer.writerow([area_count, area])
            area_ids.append(area_count)
            area_count += 1
        
        for city in cites:
            city_writer.writerow([city_count, city])
            city_ids.append(city_count)
            city_count += 1

        for area_id in area_ids:
            for city_id in city_ids:
                area_city_writer.writerow([area_id, city_id])


normalize_zip_area()
