from apps.posts import models
from apps.users.models import User, BaseModel
from django.db import models


class Rating(BaseModel):
    name = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ratings')
    post = models.ForeignKey("Post", on_delete=models.CASCADE,null=True,related_name='post_ratings')
    rating = models.PositiveIntegerField(default=0.0)

    class Meta:
        unique_together = ('user', 'post')

    def __str__(self):
        return f"{self.user.email} - {self.post.name} - {self.rating}"

class Comment(BaseModel):
    comment = models.TextField(blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_comments')
    post = models.ForeignKey("Post", on_delete=models.CASCADE,null=True, related_name='post_comments')
    
    def __str__(self):
        return f"{self.user.email} - {self.post.name} - {self.comment[:20]}"

class Post(BaseModel):
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

    def __str__(self):
        return self.name


class Location(BaseModel):
    name = models.CharField(max_length=255)
    latitude = models.FloatField()
    longitude = models.FloatField()

    def __str__(self):
        return self.name



class Category(BaseModel):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name