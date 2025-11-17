from django.apps import AppConfig


class AppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.app'
    label = 'app'

    # def ready(self):
    #     import apps.app.signals  