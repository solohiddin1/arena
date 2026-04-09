from django.contrib import admin
from django.utils.html import format_html

from apps.posts.models import Post, Feedback, Category, PostImage

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


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'owner', 'location_title', 'cost', 'state', 'is_hidden', 'average_rating', 'total_feedbacks', 'comment_count')
    search_fields = ('title', 'location_title', 'owner__email')
    list_filter = ('owner', 'state', 'is_hidden', 'region', 'district', 'category')
    actions = [make_accepted, make_cancelled, make_frozen, make_checking]

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'post', 'rating', 'comment')
    search_fields = ('name', 'comment', 'user__email', 'post__title')
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

@admin.register(PostImage)
class PostImageAdmin(admin.ModelAdmin):
    list_display = ('post', 'image_preview')
    search_fields = ('post__title',)
    readonly_fields = ('image_preview',)

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="70" height="70" style="object-fit:cover;border-radius:6px;" />', obj.image.url)
        return "-"

    image_preview.short_description = 'Preview'