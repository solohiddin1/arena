from django.db import models
# from app.models.post import Post
from app.models.user import User


class Rating(models.Model):
    name = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ratings')
    post = models.ForeignKey("Post", on_delete=models.CASCADE,null=True,related_name='post_ratings')
    rating = models.PositiveIntegerField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)