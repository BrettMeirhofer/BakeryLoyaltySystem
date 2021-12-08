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

    def _build_app_dict(self, request, label=None):
        print("Build")
        """
        Build the app dictionary. The optional `label` parameter filters models
        of a specific app.
        """
        app_dict = {}

        if label:
            models = {
                m: m_a for m, m_a in self._registry.items()
                if m._meta.app_label == label
            }
        else:
            models = self._registry
        for model, model_admin in models.items():
            app_label = model._meta.app_label
            try:
                table_label = model.category
            except AttributeError:
                table_label = app_label
            has_module_perms = model_admin.has_module_permission(request)
            if not has_module_perms:
                continue

            perms = model_admin.get_model_perms(request)

            # Check whether user has any perm for this module.
            # If so, add the module to the model_list.
            if True not in perms.values():
                continue

            info = (app_label, model._meta.model_name)
            model_dict = {
                'name': capfirst(model._meta.verbose_name_plural),
                'object_name': model._meta.object_name,
                'perms': perms,
                'admin_url': None,
                'add_url': None,
            }
            if perms.get('change') or perms.get('view'):
                model_dict['view_only'] = not perms.get('change')
                try:
                    model_dict['admin_url'] = reverse('admin:%s_%s_changelist' % info, current_app=self.name)
                except NoReverseMatch:
                    pass
            if perms.get('add'):
                try:
                    model_dict['add_url'] = reverse('admin:%s_%s_add' % info, current_app=self.name)
                except NoReverseMatch:
                    pass

            if table_label in app_dict:
                app_dict[table_label]['models'].append(model_dict)
            else:
                app_dict[table_label] = {
                    'name': table_label,
                    'app_label': app_label,

                    'has_module_perms': has_module_perms,
                    'models': [model_dict],
                }

        if label:
            return app_dict.get(label)
        return app_dict

    #Could be improved by creating a library of reports on server start instead of everytime a link is clicked
    def index(self, request, extra_context=None):
        context = {
            **self.each_context(request),
            'title': self.index_title,
            'subtitle': None,
        }

        request.current_app = self.name

        return TemplateResponse(request, self.index_template or 'admin/bakery_dash.html', context)


    def backup(self, request, extra_context=None):
        context = {
            **self.each_context(request),
            'title': "Backup",
        }

        return TemplateResponse(request, self.index_template or 'admin/backup.html', context)

    def actual_index(self, request, extra_context=None):
        app_list = self.get_app_list(request)
        module_dir = os.path.dirname(__file__)  # get current directory
        reports = views.get_report_names(module_dir)

        context = {
            **self.each_context(request),
            'title': "Bakery",
            'subtitle': None,
            'app_list': app_list,
            'report_list':  reports,
            **(extra_context or {}),
        }

        request.current_app = self.name

        return TemplateResponse(request, self.index_template or 'admin/index.html', context)

    def reports_index(self, request, extra_context=None):
        paths, names = views.get_report_paths()
        reports = [{"name": "Employees", "reports": []}, {"name": "Customers", "reports": []},
                   {"name": "Other", "reports": []}]

        for index,report in enumerate(names):
            if "employee".lower() in report.lower():
                cat = 0
            elif "customer".lower() in report.lower():
                cat = 1
            else:
                cat = 2

            reports[cat]["reports"].append({"report": report, "index": index})

        context = {
            **self.each_context(request),
            'title': "Reports",
            'subtitle': None,
            'report_list':  reports,
            **(extra_context or {}),
        }

        request.current_app = self.name

        return TemplateResponse(request, self.index_template or 'admin/reports_index.html', context)

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('loademps', self.admin_view(views.load_employees), name='loademps'),
            path('loadproducts', self.admin_view(views.load_products), name='loadproducts'),
            path('loadproductprice', self.admin_view(views.load_product_price), name='loadproductprice'),
            path('loadrewards', self.admin_view(views.load_rewards), name='loadrewards'),
            path('load_reward_details', self.admin_view(views.load_reward_details), name='load_reward_details'),
            path('load_states', self.admin_view(views.load_states), name='load_states'),
            path('Bakery/', self.admin_view(self.actual_index), name='Bakery'),
            path('reports/', self.admin_view(self.reports_index), name='reports'),
            path('report/<int:index>/', self.admin_view(views.html_report), name="report"),
            path('top_products_month', self.admin_view(views.top_products_month), name='top_products_month'),
            path('top_emps_month', self.admin_view(views.top_emps_month), name='top_emps_month'),
            path('top_cust_month', self.admin_view(views.top_cust_month), name='top_cust_month'),
            path('backup', self.admin_view(self.backup), name='backup'),

        ]
        return my_urls + urls
