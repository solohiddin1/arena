from apps.posts import models
from apps.users.models import User
from django.db import models


class Rating(models.Model):
    name = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ratings')
    post = models.ForeignKey("Post", on_delete=models.CASCADE,null=True,related_name='post_ratings')
    rating = models.PositiveIntegerField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)



class Comment(models.Model):
    comment = models.TextField(blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_comments')
    post = models.ForeignKey("Post", on_delete=models.CASCADE,null=True, related_name='post_comments')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Post(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=255)
    images = models.ImageField(upload_to="photos/", height_field=None, width_field=None, max_length=None, default='photos/default.jpg')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    open_time = models.TimeField()
    close_time = models.TimeField()
    rating = models.ForeignKey(Rating, on_delete=models.CASCADE, default=0.0,related_name='post_ratings')
    comments = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='post_comments', blank=True, null=True)
    comment_count = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)




class Location(models.Model):
    name = models.CharField(max_length=255)
    latitude = models.FloatField()
    longitude = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name





class Category(models.Model):
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name