from django.contrib import admin

from app.models.arena import Arena
from .models.owner import Owner
from .models.user import User
from .models.ratings import Rating
from .models.comment import Comment


# Register your models here.

# admin.site.register(Student)
admin.site.register(User)
admin.site.register(Arena)
admin.site.register(Owner)
admin.site.register(Rating)
admin.site.register(Comment)