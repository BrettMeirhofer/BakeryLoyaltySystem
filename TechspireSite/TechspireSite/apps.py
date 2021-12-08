from django.contrib.admin.apps import AdminConfig


class TechSpireAdminConfig(AdminConfig):
    default_site = 'TechspireSite.admin.TechSpireAdminSite'
