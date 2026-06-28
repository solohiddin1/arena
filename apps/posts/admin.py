from django.contrib import admin
from django.utils.html import format_html
from gunicorn.config import Workers
from parler.admin import TranslatableAdmin

from apps.posts.models import Post, Feedback, Category, PostImage, PostWorkDays, Amenity, PostCertificate, AppFeedback, Favourite, AdminNotification

def make_accepted(modeladmin, request, queryset):
    queryset.update(state='ACCEPTED')
make_accepted.short_description = "Mark ACCEPTED"

def make_cancelled(modeladmin, request, queryset):
    queryset.update(state='CANCELLED')
make_cancelled.short_description = "Mark CANCELLED"

def make_frozen(modeladmin, request, queryset):
    queryset.update(state='FROZEN')
make_frozen.short_description = "Mark FROZEN"

def make_checking(modeladmin, request, queryset):
    queryset.update(state='CHECKING')
make_checking.short_description = "Mark CHECKING"

class WorkHoursInline(admin.TabularInline):
    model = PostWorkDays
    extra = 0

class PostCertificateInline(admin.TabularInline):
    model = PostCertificate
    extra = 0
    readonly_fields = ('image_preview',)

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="70" height="70" style="object-fit:cover;border-radius:6px;" />', obj.image.url)
        return "-"
    image_preview.short_description = 'Preview'

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'owner', 'phone_number', 'state', 'is_hidden', 'average_rating', 'total_feedbacks', 'comment_count')
    search_fields = ('title', 'location_title', 'owner__email', 'phone_number')
    list_filter = ('owner', 'state', 'is_hidden', 'region', 'district', 'category', 'social_media_type')
    actions = [make_accepted, make_cancelled, make_frozen, make_checking]
    inlines = [WorkHoursInline, PostCertificateInline]
    fieldsets = (
        (None, {
            'fields': ('title', 'description', 'owner', 'state', 'is_hidden')
        }),
        ('Location', {
            'fields': ('location_title', 'lat', 'long', 'region', 'district')
        }),
        ('Contact & Social', {
            'fields': ('phone_number', 'social_media_link', 'social_media_type')
        }),
        ('Details', {
            'fields': ('category', 'amenities', 'prices', 'comment_count')
        }),
    )


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'rating', 'comment')
    search_fields = ('comment', 'user__email', 'post__title')
    list_filter = ('user', 'post')

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'image_preview')
    search_fields = ('title',)
    readonly_fields = ('image_preview',)

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="70" height="70" style="object-fit:cover;border-radius:6px;" />', obj.image.url)
        return "-"

    image_preview.short_description = 'Preview'

@admin.register(Amenity)
class AmenityAdmin(TranslatableAdmin):
    # list_display = ('title', 'is_positive')
    # search_fields = ('translations__title',)
    list_filter = ('is_positive',)


@admin.register(PostCertificate)
class PostCertificateAdmin(admin.ModelAdmin):
    list_display = ('post', 'image_preview')
    search_fields = ('post__title',)
    readonly_fields = ('image_preview',)

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="70" height="70" style="object-fit:cover;border-radius:6px;" />', obj.image.url)
        return "-"

    image_preview.short_description = 'Preview'


@admin.register(AppFeedback)
class AppFeedbackAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'rating', 'short_message', 'created_at')
    search_fields = ('user__email', 'message')
    list_filter = ('rating',)
    readonly_fields = ('user', 'message', 'rating', 'created_at')

    def short_message(self, obj):
        return obj.message[:80] + '...' if len(obj.message) > 80 else obj.message
    short_message.short_description = 'Message'


@admin.register(Favourite)
class FavouriteAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'post', 'created_at')
    search_fields = ('user__email', 'post__title')
    list_filter = ('created_at',)


def mark_as_read(modeladmin, request, queryset):
    queryset.update(is_read=True)
mark_as_read.short_description = "Mark selected as read"


@admin.register(AdminNotification)
class AdminNotificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'type', 'short_message', 'is_read', 'created_at')
    list_filter = ('type', 'is_read')
    search_fields = ('message',)
    actions = [mark_as_read]
    readonly_fields = ('type', 'message', 'object_id', 'created_at')

    def short_message(self, obj):
        return obj.message[:100] + '...' if len(obj.message) > 100 else obj.message
    short_message.short_description = 'Message'

    def get_queryset(self, request):
        return super().get_queryset(request).order_by('-created_at')