from django.contrib import admin
from django.urls import path
from django.template.response import TemplateResponse
from . import views
from django.urls import NoReverseMatch, Resolver404, resolve, reverse
from django.apps import apps
from django.utils.text import capfirst
import os
from django.template.defaulttags import register


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


class AdminTableRow:
    path = ""
    name = ""

    def __init__(self, in_path, in_name):
        self.path = in_path
        self.name = in_name


class SubApp:
    app_url = ""
    app_label = "Test"
    models = []

    def __init__(self, app_url, app_label):
        self.app_url = app_url
        self.app_label = app_label


class TechSpireAdminSite(admin.AdminSite):
    site_header = "Hot Breads Admin"
    site_title = "Hot Breads Admin"
    index_title = "Welcome to Hot Breads Admin"

    def backup(self, request, extra_context=None):
        context = {
            **self.each_context(request),
            'title': "Backup",
        }

        return TemplateResponse(request, self.index_template or 'admin/backup.html', context)

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('loadproducts', self.admin_view(views.load_products), name='loadproducts'),
            path('loadproductprice', self.admin_view(views.load_product_price), name='loadproductprice'),
            path('loadrewards', self.admin_view(views.load_rewards), name='loadrewards'),
            path('load_reward_details', self.admin_view(views.load_reward_details), name='load_reward_details'),
            path('top_products_month', self.admin_view(views.top_products_month), name='top_products_month'),
            path('top_cust_month', self.admin_view(views.top_cust_month), name='top_cust_month'),
            path('backup', self.admin_view(self.backup), name='backup'),

        ]
        return my_urls + urls
