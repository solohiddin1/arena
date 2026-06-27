from rest_framework import serializers

from apps.posts.models import Favourite, Post
from apps.posts.api.serializers.post import PostBaseSerializer


class FavouriteWriteSerializer(serializers.Serializer):
    post_id = serializers.IntegerField(required=True)


class FavouriteReadSerializer(serializers.ModelSerializer):
    post = PostBaseSerializer(read_only=True)

    class Meta:
        model = Favourite
        fields = ("id", "post", "created_at")