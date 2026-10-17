from django.contrib.admin.apps import AdminConfig
from django.contrib import admin

class CustomAdminSite(admin.AdminSite):
    def get_app_list(self, request, app_label=None):
        app_dict = self._build_app_dict(request, app_label)

        app_ordering = {
            "users": 1,
            "posts": 2,
            "shared": 3,
            "notification": 4,
            "auth": 5,
            "token_blacklist": 6,
        }

        app_list = sorted(
            app_dict.values(),
            key=lambda x: app_ordering.get(x['app_label'], float('inf'))
        )

        return app_list

class MyAdminConfig(AdminConfig):
    default_site = 'arena.admin_site.CustomAdminSite'