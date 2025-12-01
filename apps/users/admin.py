from django.contrib import admin
from .models import User, UserAuthOtp , UserDevice, VersionControl, OtpSentLog, UserPasswordReset
from django.utils.html import format_html

# Register your models here.

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['id', 'email', 'phone_number', 'is_staff', 'is_active', 'is_superuser', 'is_verified', 'show_avatar']
    search_fields = ['email', 'phone_number']

    def show_avatar(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="40" style="border-radius: 50%;" />', obj.image.url)
        return "-"


@admin.register(UserDevice)
class UserDeviceAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'role', 'device_id', 'device_type']


@admin.register(VersionControl)
class VersionControlAdmin(admin.ModelAdmin):
    list_display = ['id', 'device_type', 'current_version', 'is_active', 'force_update', 'updated_at']


@admin.register(UserAuthOtp)
class UserAuthOtpAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'code', 'is_used', 'incorrect_count', 'verified']


@admin.register(OtpSentLog)
class OtpSentLogAdmin(admin.ModelAdmin):
    list_display = ['id', 'email', 'message_id', 'otp']

@admin.register(UserPasswordReset)
class UserPasswordResetAdmin(admin.ModelAdmin):
    list_display = ['id','user','reset_token','reset_token_created_at','code','otp_created_at','incorrect_count','otp_count','verified']