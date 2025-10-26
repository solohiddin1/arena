from django.contrib import admin

from app.models.post import Post
from .models.owner import Owner
from .models.user import User
from .models.ratings import Rating
from .models.comment import Comment


# Register your models here.

# admin.site.register(Student)
admin.site.register(User)
admin.site.register(Post)
admin.site.register(Owner)
admin.site.register(Rating)
admin.site.register(Comment)