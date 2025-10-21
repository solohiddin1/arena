from django.db import models
from .owner import Owner
from .ratings import Rating
from .comment import Comment

class Arena(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=255)
    image = models.ImageField(upload_to="photos/", height_field=None, width_field=None, max_length=None, default='photos/default.jpg')
    owner = models.ForeignKey(Owner, on_delete=models.CASCADE, related_name='arenas')
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    open_time = models.TimeField()
    close_time = models.TimeField()
    # rating = models.ForeignKey(Rating, on_delete=models.CASCADE, default=0.0)
    # comments = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='arenas', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)