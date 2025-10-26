from django.db import models
from .user import User
# from .post import Post


class Comment(models.Model):
    comment = models.TextField(blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_comments')
    post = models.ForeignKey("Post", on_delete=models.CASCADE,null=True, related_name='post_comments')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)