from django.db import models
from .user import User

class Owner(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    arena_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.name if self.user.name else self.user.email