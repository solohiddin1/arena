from django.contrib import admin
from apps.posts.models import Post, Rating, Comment, Location, Category

# Register your models here.

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'location', 'cost', 'open_time', 'close_time', 'rating', 'comment_count')
    search_fields = ('name', 'location', 'owner__email')
    list_filter = ('owner',)

@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'post', 'rating')
    search_fields = ('name', 'user__email', 'post__name')
    list_filter = ('user', 'post')

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('comment', 'user', 'post')
    search_fields = ('comment', 'user__email', 'post__name')
    list_filter = ('user', 'post')

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'latitude', 'longitude')
    search_fields = ('name',)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)