from django.contrib import admin
from .models import User, UserAuthOtp , UserDevice
from django.utils.html import format_html

# Register your models here.

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['id', 'email', 'phone_number', 'is_staff', 'is_active', 'is_superuser', 'is_verified', 'show_avatar']
    search_fields = ['email', 'phone_number']

    def show_avatar(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" style="border-radius: 50%;" />', obj.image.url)
        return "-"


@admin.register(UserDevice)
class UserDeviceAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'role', 'device_id', 'device_type']


@admin.register(UserAuthOtp)
class UserAuthOtpAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'code', 'is_used', 'incorrect_count', 'verified']
