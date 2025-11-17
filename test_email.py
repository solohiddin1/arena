import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "arena.settings")
django.setup()

from apps.users.repository import send_otp_email

send_otp_email("sirojiddinovsolohiddin5@gmail.com",1122)