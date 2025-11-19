from django.contrib import admin
from .models import Service, ServiceWishlist, StaffSeller, \
    ServiceWorkDays , StaffSeller, BusinessStatusEnum, Submission, \
    BusinessCategory, BusinessType, ViewerTypeEnum, Banner

# Register your models here.
from parler.admin import TranslatableAdmin
from django.utils.html import format_html


class WorkDaysInline(admin.TabularInline):
    model = ServiceWorkDays
    extra = 1


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'state', 'phone_number', 'is_active', 'region', 'district', 'address', 'created_at',
                    'image_preview']
    list_filter = ['state', 'is_active']
    search_fields = ['title']
    inlines = [WorkDaysInline]
    readonly_fields = ['image_preview']
    # filter_horizontal = ("categories",)

    def image_preview(self, obj):
        if obj and obj.image:
            return format_html('<img src="{}" style="max-height:60px;"/>', obj.image.url)
        return "-"

    image_preview.short_description = "Image"

    def get_model_perms(self, request):
        perms = super().get_model_perms(request)
        count = Service.objects.filter(state="checking").count()
        self.model._meta.verbose_name_plural = f"Service  ({count})"
        return perms


@admin.register(BusinessCategory)
class BusinessCategoryAdmin(TranslatableAdmin):
    list_display = ['id', 'name', 'is_active', 'image_preview']
    readonly_fields=['image_preview']

    def image_preview(self, obj):
        if obj and obj.image:
            return format_html('<img src="{}" style="max-height:60px;"/>', obj.image.url)
        return "-"

@admin.register(StaffSeller)
class SellerAdmin(admin.ModelAdmin):
    list_display = ['username', 'phone_number']


@admin.register(ServiceWorkDays)
class WorkDayAdmin(admin.ModelAdmin):
    list_display = ['service', 'day_of_week', 'start_time', 'end_time', 'is_closed']


@admin.register(BusinessType)
class BusinessTypeAdmin(TranslatableAdmin):
    list_display = ['id', 'name', 'hint_text', 'title', 'inn_lenth']


# @admin.register(Comission)
# class ComissionAdmin(admin.ModelAdmin):
#     list_display = ['name', ]


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ['mxik_code', 'category_name', 'description', 'applied_at', 'applied', 'parend']


@admin.register(Banner)
class BannerAdmin(TranslatableAdmin):
    list_display = ['name', 'image', 'link', 'is_active', 'service']
