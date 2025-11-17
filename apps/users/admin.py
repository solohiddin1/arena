from django.contrib import admin
from .models import User, UserRole, UserAuthOtp , UserDevice, VersionControl
from django.utils.html import format_html

# Register your models here.

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['id', 'email', 'phone_number', 'password', 'is_staff', 'is_active', 'is_superuser', 'show_avatar']
    search_fields = ['email', 'phone_number']

    def show_avatar(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="40" style="border-radius: 50%;" />', obj.image.url)
        return "-"


@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'role', 'is_active', 'is_verified']
    search_fields = ['user__email', 'user__phone_number', 'user__email']


@admin.register(UserDevice)
class Admin(admin.ModelAdmin):
    list_display = ['id', 'user', 'role', 'device_id', 'device_type']


@admin.register(VersionControl)
class VersionControlAdmin(admin.ModelAdmin):
    list_display = ['id', 'device_type', 'current_version', 'is_active', 'force_update', 'updated_at']
