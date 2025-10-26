from rest_framework import serializers
from app.models.post import Post

class ArenaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['name', 'location', 'images', 'owner', 'cost', 'open_time', 'close_time',"rating","comments","comment_count",]
        read_only_fields = ['id','created_at', 'updated_at']