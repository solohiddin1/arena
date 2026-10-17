from django.contrib import admin
from .models import User, UserAuthOtp, UserDevice, Device, TelegramLoginToken
from django.utils.html import format_html

# Register your models here.

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['id', 'email', 'phone_number', 'telegram_id', 'is_staff', 'is_active', 'is_superuser', 'is_verified', 'show_avatar']
    search_fields = ['email', 'phone_number', 'telegram_id', 'telegram_username']

    def show_avatar(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" style="border-radius: 50%;" />', obj.image.url)
        return "-"


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'user', 'device_type', 'device_id', 'is_active', 'created_at']
    list_filter = ['device_type', 'is_active']
    search_fields = ['name', 'device_id', 'user__email', 'user__phone_number']


@admin.register(TelegramLoginToken)
class TelegramLoginTokenAdmin(admin.ModelAdmin):
    list_display = ['id', 'token', 'status', 'telegram_id', 'user', 'otp_mode', 'expires_at', 'created_at']
    list_filter = ['status', 'otp_mode']
    search_fields = ['token', 'telegram_id']


@admin.register(UserDevice)
class UserDeviceAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'role', 'device_id', 'device_type']


@admin.register(UserAuthOtp)
class UserAuthOtpAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'code', 'is_used', 'incorrect_count', 'verified']
