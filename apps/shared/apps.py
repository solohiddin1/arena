import time
from django.apps import AppConfig
from django.conf import settings


class SharedConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.shared'

    def ready(self):
        import os
        if os.environ.get('RUN_MAIN') == 'true':
            boot_duration = time.time() - settings.START_TIME
            print(f"Server started in {boot_duration:.3f} seconds!\n")
