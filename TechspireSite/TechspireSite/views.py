from . import data_dict_helper as ddh
from django.http import HttpResponse
from django.shortcuts import render
from django.db import connection, ProgrammingError, DataError
from operator import itemgetter
from django.apps import apps
from Bakery.models import Store, Product, Reward
from django.db import models
import glob
import os
import json
import functools
import operator


# Opens an sql file in the Sql/Admin Folder
def open_admin_sql(file):
    module_dir = os.path.dirname(__file__)
    path = os.path.join(module_dir, "SQL", "Admin", file)
    return open(path, "r")


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


def top_cust_month(request):
    return get_graph_data("QueryCustPerfMonthly.sql")

