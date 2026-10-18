from django.contrib import admin
from .models import Region , District
# Register your models here.


@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ['id', 'name_uz', 'name_ru', 'name_en']
    search_fields = ['name_uz', 'name_ru', 'name_en']


@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    list_display = ['id', 'name_uz', 'name_ru', 'name_en', 'region']
    search_fields = ['name_uz', 'name_ru', 'name_en']
    list_filter = ['region']


from .models import SiteConfig


@admin.register(SiteConfig)
class SiteConfigAdmin(admin.ModelAdmin):
    list_display = ('id', 'send_otp_code', 'otp_wait_seconds', 'otp_timeout_seconds', 'created_at', 'updated_at')
    list_editable = ('send_otp_code', 'otp_wait_seconds', 'otp_timeout_seconds')