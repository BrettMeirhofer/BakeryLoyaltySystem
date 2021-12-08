from . import data_dict_helper as ddh
from django.http import HttpResponse
from django.shortcuts import render
from django.db import connection, ProgrammingError, DataError
from operator import itemgetter
from django.apps import apps
from Bakery.models import Employee, EmployeeJob, Store, Product, Reward, StateProvince, Location
from django.db import models
import glob
import os
import json
import functools
import operator


class FieldTypeMap:
    field_type_dict = {"CharField": "nvarchar", "DateField": "date", "BooleanField": "bit", "BigAutoField": "bigint",
                       "EmailField": "nvarchar", "TextField": "nvarchar", "ForeignKey": "int", "IntegerField": "int",
                       "DecimalField": "numeric", "AutoField": "int", "PhoneNumberField": "nvarchar"}


# Builds the names/paths used for the Reports Index page
def get_report_paths():
    module_dir = os.path.dirname(__file__)
    paths = get_reports(module_dir)
    out = []

    for path in paths:
        name = open(path).readlines()[1]
        name = name.replace("--", "")
        out.append([name, path])
    out.sort(key=lambda x: x[0].replace(" ", ""))
    paths = []
    names = []
    for element in out:
        paths.append(element[1])
        names.append(element[0])
    return paths, names


def erd1(request):
    return ddh.generate_erd("GeneratedFiles", "ERD1", "crow", True)


# Displays a page with all the props for each field of each model as a table
def dict1(request):
    context = {"titles": ["Table Name", "Row Name", "Row Desc", "Default", "Max Length", "Type", "PK", "FK",
                          "Required", "Allow NULL", "C Delete", "C Update", "Domain"], "tables": []}
    blank_row = []
    for index in enumerate(context["titles"]):
        blank_row.append(" ")
    model_list = apps.get_app_config('Bakery').get_models()
    for model in model_list:
        model_name = model._meta.db_table
        field_props = ddh.extract_all_field_props(model, FieldTypeMap.field_type_dict)
        for count, row in enumerate(field_props):
            if count == 0:
                row.insert(0, model_name)
            else:
                row.insert(0, " ")
        context["tables"] = context["tables"] + field_props
        context["tables"].append(blank_row)
    return render(request, 'admin/reports/display_report.html', context)


# Displays a page with the name and description of each model
def dict2(request):
    context = {"titles": ["Table Name", "Table Desc", "Owner", "Load Order"], "tables": []}
    model_list = apps.get_app_config('Bakery').get_models()
    for model in model_list:
        model_object = model()
        model_name = model._meta.db_table
        model_desc = model_object.description
        context["tables"].append([model_name, model_desc, model.owner.name, model.load_order])

    context["tables"] = sorted(context["tables"], key=itemgetter(2))
    app = apps.get_app_config("Bakery")

    models = app.models.values()
    models = [item() for item in models]
    valid_tables = [item for item in models if not item._meta.abstract]
    foreign_count = 0
    for table in valid_tables:
        model_fields = table._meta.get_fields(include_parents=False)
        for field in model_fields:
            name = type(field).__name__
            if name == "ForeignKey":
                foreign_count += 1
            else:
                pass
    foreign_count = "Foreign Keys: " + str(foreign_count)
    table_count = "Table count: " + str(len(valid_tables))

    context["extra_info"] = [table_count, foreign_count]
    return render(request, 'admin/display_table.html', context)


# Gets a list of reports within the SQL folder
def get_reports(path):
    return glob.glob(os.path.join(path, "SQL/*/Report*"))


# Gets a list of names for the reports in the SQL folder
def get_report_names(path):
    reports = get_reports(path)
    out_names = []
    for report in reports:
        out_names.append(open(report).readlines()[1].replace("--", ""))
    return out_names


# Creates a download for a data dictionary excel file
# Title row could be passed as a parameter
# Majority of function could be extracted into a different file
def dict3(request):
    title_row = ["Load Order", "Owner", "Table Name", "Row Name", "Default", "Max Length", "Type", "PK", "FK",
                 "Required", "Allow NULL", "C Delete", "C Update", "Domain", "Row Desc", "Table Desc"]
    module_dir = os.path.dirname(__file__)
    file_path = os.path.join(module_dir, "GeneratedFiles", "DataDict.xlsx")
    ddh.generate_data_dict_excel(file_path, title_row, FieldTypeMap.field_type_dict)
    final_sheet = open(file_path, "rb")
    response = HttpResponse(final_sheet,
                            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    return response


# Generates an html page for a single report
# Could be improved by creating a library of reports on server start instead of everytime a link is clicked
def html_report(request, index):
    paths, names = get_report_paths()
    file_path = paths[index]
    context = {"reports": [build_report_obj(file_path)]}
    return render(request, 'admin/reports/display_report.html', context)


# Generates a correctly ordered drop script
def generate_drop(request):
    ddh.generate_ordered_sql("Bakery", True, "DROP TABLE", "Drop.sql")
    return HttpResponse("Success")


# Generates a correctly ordered delete script
def generate_delete(request):
    ddh.generate_ordered_sql("Bakery", True, "DELETE FROM", "Delete.sql")
    return HttpResponse("Success")


# Copies everything from the path file into the bulk_file
def copy_from_file(path, bulk_file):
    file = open(path, "r")
    bulk_file.writelines(["\n"])
    bulk_file.writelines(file.readlines())
    file.close()


# Creates a path to the SQL folder
def sql_path(owner, file):
    module_dir = os.path.dirname(__file__)
    return os.path.join(module_dir, "SQL", owner, file + ".sql")


# Combines the bulk insert for every model into a single SQL file
def generate_bulk(request):
    solid_tables = ddh.get_solid_models("Bakery")
    solid_tables.sort(key=lambda x: x.load_order)
    module_dir = os.path.dirname(__file__)
    bulk_paths = glob.glob(os.path.join(module_dir, "SQL/*/BulkInsert*"))
    path_dict = {}
    for path in bulk_paths:
        name = os.path.basename(path).replace("BulkInsert", "")[:-4]
        path_dict[name] = path
    path = os.path.join(module_dir, "SQL", "BulkInsert.sql")
    bulk_file = open(path, "w")
    for table in solid_tables:
        try:
            table.bulk_insert
        except AttributeError:
            bulk_path = path_dict[table._meta.db_table]
            current_bulk_file = open(bulk_path, "r")
            bulk_file.write("--" + table.owner.name + "\n")
            bulk_file.writelines(current_bulk_file.readlines())
            bulk_file.write("\n\n")

    brett_scripts = ["UpdateOrderRewards", "UpdateOrderTotals", "InsertCalculatedPointLogs",
                     "InsertManualPointLogs", "UpdateCustomerPoints", "UpdateCustomerTier"]
    for script in brett_scripts:
        copy_from_file(sql_path("Brett M", script), bulk_file)

    copy_from_file(sql_path("Kyle D", "UpdateEmployeeEmployeeCategory"), bulk_file)
    copy_from_file(sql_path("Rebecca H", "UpdateCustomerCustomerCategory"), bulk_file)
    return HttpResponse("Success")


# Displays which models have a data file for importing purposes
def data_status(request):
    context = {"titles": ["Table", "Data Status"], "tables": []}

    module_dir = os.path.dirname(__file__)
    bulk_paths = glob.glob(os.path.join(module_dir, "SQL/*/*List.tsv"))
    path_dict = {}
    for path in bulk_paths:
        name = os.path.basename(path).replace("List", "")[:-4]
        path_dict[name] = path

    solid_tables = ddh.get_solid_models("Bakery")
    for table in solid_tables:
        try:
            var = path_dict[table._meta.db_table]
            status = "Available"
        except KeyError:
            status = "Not Available"
        context["tables"].append([table._meta.db_table, status])
    context["tables"].sort(key=itemgetter(1))
    return render(request, 'admin/reports/display_report.html', context)


# Holds output and meta data for a specific report
class ReportData:
    owner = ""
    name = ""
    rule = ""
    desc = ""
    data = []
    titles = []
    sql = []

    def __init__(self, owner, name, rule, data, titles, sql, desc):
        self.owner = owner
        self.name = name
        self.rule = rule
        self.data = data
        self.titles = titles
        self.sql = sql
        self.desc = desc


# Extracts report metadata and output to a ReportData object
def build_report_obj(path):
    with open(path, "r") as report_object:
        report_text = report_object.readlines()

    owner = report_text.pop(0).replace("--", "")
    name = report_text.pop(0).replace("--", "")
    rule = report_text.pop(0).replace("--", "")
    desc = report_text.pop(0).replace("--", "")
    titles = report_text.pop(0).replace("--", "").split(",")
    align = report_text.pop(0).replace("--", "").replace("\n", "").split(",")

    with open(path, "r") as report_object:
        sql = report_object.read()

    with connection.cursor() as cursor:
        cursor.execute(sql)
        output = cursor.fetchall()

        new_output = []
        for row in output:
            new_row = []
            for index, column in enumerate(row):
                col_class = align[index]
                new_row.append([column, col_class])
            new_output.append(new_row)

    report_data = ReportData(owner, name, rule, new_output, titles, report_text, desc)
    return report_data


# Merges all reports into a single html file
def generate_final_report(request):
    module_dir = os.path.dirname(__file__)  # get current directory
    reports = get_reports(module_dir)
    context = {"reports": []}
    for report in reports:
        file_path = os.path.join(module_dir, report)
        build_report_obj(file_path)
        context["reports"].append(build_report_obj(file_path))

    return render(request, 'admin/reports/final_report.html', context)


# Lists all reports within the SQL. Displays name, owner, and status of each report.
def report_status(request):
    context = {"titles": ["Report Name", "Owner", "Status", "Rows"], "tables": []}
    module_dir = os.path.dirname(__file__)
    reports = get_reports(module_dir)
    for report in reports:
        file_path = os.path.join(module_dir, report)
        rows = 0
        try:
            obj = build_report_obj(file_path)
            rows = len(obj.data)
            status = "Success"
        except ProgrammingError as e:
            status = "Invalid"
        except DataError:
            status = "Invalid"
        except IndexError:
            status = "Missing Alignment Row"
        owner = os.path.basename(os.path.dirname(file_path))
        name = os.path.basename(file_path)
        context["tables"].append([name, owner, status, rows])
    num_reports = len(context["tables"])
    num_reports = "Num reports: " + str(num_reports)
    num_errors = 0
    for row in context["tables"]:
        if row[2] == "Invalid":
            num_errors += 1
    num_errors = "Num Errors: " + str(num_errors)
    context["extra_info"] = [num_reports, num_errors]
    return render(request, 'admin/display_table.html', context)


# Opens an sql file in the Sql/Admin Folder
def open_admin_sql(file):
    module_dir = os.path.dirname(__file__)
    path = os.path.join(module_dir, "SQL", "Admin", file)
    return open(path, "r")


# Renders employee dropdowns based on store
def load_employees(request):
    store_id = request.GET.get('store')
    sql = open_admin_sql("QueryStoreCashiers.sql")
    emps = Employee.objects.raw(sql.read(), [store_id, ])
    return render(request, 'admin/update_drop_down.html', {'options': emps})


# Renders product dropdowns based on store
def load_products(request):
    store_id = request.GET.get('store')
    sql = open_admin_sql("QueryStoreProducts.sql")
    products = Product.objects.raw(sql.read(), [store_id, ])
    return render(request, 'admin/update_drop_down.html', {'options': products})


# Returns the price/loyalty system status of a specific product
def load_product_price(request):
    product_id = request.GET.get("product")
    response_data = {}
    eligible = False
    try:
        target_obj = Product.objects.get(pk=product_id)
        price = target_obj.product_price
        eligible = target_obj.ban_reason_id
    except Product.DoesNotExist:
        price = 0
        eligible = False
    except ValueError:
        price = 0
        eligible = False
    response_data["price"] = str(price)
    response_data["eligible"] = str(eligible)
    return HttpResponse(json.dumps(response_data), content_type="application/json")


# Renders reward dropdowns based on store
def load_rewards(request):
    # customer_id = request.GET.get('customer')
    print("Recieved Rewards Request")
    store_id = request.GET.get('store')
    sql = open_admin_sql("QueryStoreRewards.sql")
    rewards = Reward.objects.raw(sql.read(), [store_id])
    return render(request, 'admin/update_drop_down.html', {'options': rewards})


# Renders json for a specific reward row
def load_reward_details(request):
    reward_id = request.GET.get("reward")
    response_data = {"discount": 0, "cost": 0, "product": ""}
    try:
        target_reward = Reward.objects.get(pk=reward_id)
        response_data["discount"] = str(target_reward.discount_amount)
        response_data["cost"] = str(target_reward.point_cost)
        response_data["product"] = str(target_reward.free_product)
    except Reward.DoesNotExist:
        pass
    except ValueError:
        pass
    return HttpResponse(json.dumps(response_data), content_type="application/json")


# Renders state dropdowns based on country
def load_states(request):
    context = {}
    country_id = request.GET.get("country")
    try:
        location = request.GET.get("location")
        selected_id = Location.objects.get(pk=location).state_id
        context["selected"] = selected_id
    except ValueError:
        # If there is no selection then don't add selected to the context
        pass
    states = StateProvince.objects.filter(country_id=country_id).order_by("state_name")
    context["options"] = states
    return render(request, 'admin/update_drop_down.html', context)


# Takes a query file and generates json data with label/y lists
def get_graph_data(file):
    module_dir = os.path.dirname(__file__)
    path = os.path.join(os.path.dirname(module_dir), "TechspireSite", "SQL", "Admin",
                        file)
    sql = open(path).read()
    with connection.cursor() as cursor:
        cursor.execute(sql)
        sql_output = cursor.fetchall()

    response_data = {"label": [], "y": []}
    for row in sql_output:
        response_data["label"].append(row[0])
        response_data["y"].append(str(row[1]))
    return HttpResponse(json.dumps(response_data), content_type="application/json")


def top_products_month(request):
    return get_graph_data("QueryProductSoldMonthly.sql")


def top_emps_month(request):
    return get_graph_data("QueryEmpPerfMonthly.sql")


def top_cust_month(request):
    return get_graph_data("QueryCustPerfMonthly.sql")


# Generates a webpage listing all the data in the database.
# Do not connect any format parameters to any sort of user input
def generate_data_document(request):
    context = {"reports": []}
    solid_tables = ddh.get_solid_models("Bakery")

    for table in solid_tables:
        model_row = {"titles": [], "name": table._meta.db_table}
        model_fields = table._meta.get_fields(include_parents=False)

        with connection.cursor() as cursor:
            sql = "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '{}'".format(
                model_row["name"])
            cursor.execute(sql)
            model_row["titles"] = cursor.fetchall()
            model_row["titles"] = functools.reduce(operator.iconcat, model_row["titles"])
            print(model_row["titles"])
            sql = 'SELECT * FROM "{}"'.format(model_row["name"])
            cursor.execute(sql)
            sql_output = cursor.fetchall()
            new_output = []
            for row in sql_output:
                new_row = []
                for index, column in enumerate(row):
                    col_class = ""
                    if column is None:
                        column = "Null"
                    new_row.append([column, col_class])
                new_output.append(new_row)
            model_row["data"] = new_output

        context["reports"].append(model_row)

    return render(request, 'admin/reports/display_report.html', context)
