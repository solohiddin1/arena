import json

from rest_framework import serializers

from apps.posts.models import Category, Post, PostImage, PostWorkDays
from apps.users.api.serializers.profile import UserProfileSerializer
from apps.shared.serializers import PostRegionSerializer, PostDistrictSerializer


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("id", "title", "image")


class PostWorkDaysSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostWorkDays
        fields = ("id", "day_of_week", "start_time", "end_time", "is_closed", "is_full_time")


class WorkHoursGroupSerializer(serializers.Serializer):
    days = serializers.ListField(
        child=serializers.ChoiceField(choices=[d[0] for d in PostWorkDays.DAYS_OF_WEEK]),
        min_length=1,
    )
    start_time = serializers.TimeField(required=False, allow_null=True)
    end_time = serializers.TimeField(required=False, allow_null=True)
    is_closed = serializers.BooleanField(default=False, required=False)
    is_full_time = serializers.BooleanField(default=False, required=False)


class PostImagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostImage
        fields = ("post", "image", "image_compressed")


class PostBaseSerializer(serializers.ModelSerializer):
    average_rating = serializers.SerializerMethodField()
    total_feedbacks = serializers.IntegerField(read_only=True)
    distance_km = serializers.SerializerMethodField()
    owner = UserProfileSerializer(read_only=True)
    region = PostRegionSerializer(read_only=True)
    district = PostDistrictSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    images = serializers.SerializerMethodField()
    work_days = PostWorkDaysSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        fields = (
            "id",
            "title",
            "location_title",
            "images",
            "cost",
            "lat",
            "long",
            "state",
            "comment_count",
            "owner",
            "region",
            "district",
            "category",
            "average_rating",
            "total_feedbacks",
            "distance_km",
            "work_days",
            "created_at",
            "updated_at",
        )

    def get_distance_km(self, obj):
        return getattr(obj, "distance_km", None)

    def get_average_rating(self, obj):
        annotated_value = getattr(obj, "avg_rating_value", None)
        if annotated_value is not None:
            return float(annotated_value)
        return obj.average_rating

    def get_images(self, obj):
        images = obj.post_images.all()
        return PostImagesSerializer(images, many=True, context=self.context).data


class PostListSerializer(PostBaseSerializer):
    related_posts = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = (
            "id",
            "title",
            "location_title",
            "images",
            "cost",
            "lat",
            "long",
            "state",
            "comment_count",
            "owner",
            "region",
            "district",
            "category",
            "average_rating",
            "total_feedbacks",
            "distance_km",
            "work_days",
            "created_at",
            "updated_at",
            "related_posts",
        )

    def get_related_posts(self, obj):
        related_posts = Post.objects.filter(
            category=obj.category,
            state='ACCEPTED',
            is_hidden=False
        ).exclude(id=obj.id).order_by('-created_at')[:5]

        return PostBaseSerializer(related_posts, many=True, context=self.context).data
        

class PostWriteSerializer(serializers.ModelSerializer):
    work_hours = serializers.CharField(required=False, allow_null=True, write_only=True)

    class Meta:
        model = Post
        fields = (
            "title",
            "location_title",
            "cost",
            "lat",
            "long",
            "region",
            "district",
            "category",
            "work_hours",
        )

    def validate_work_hours(self, value):
        if value is None:
            return None
        if isinstance(value, str):
            try:
                value = json.loads(value)
            except json.JSONDecodeError:
                raise serializers.ValidationError("Invalid JSON.")
        s = WorkHoursGroupSerializer(data=value, many=True)
        s.is_valid(raise_exception=True)
        return list(s.validated_data)

    def validate(self, attrs):
        lat = attrs.get("lat")
        long = attrs.get("long")

        if lat is not None and not (-90 <= lat <= 90):
            raise serializers.ValidationError({"lat": "Latitude must be between -90 and 90."})

        if long is not None and not (-180 <= long <= 180):
            raise serializers.ValidationError({"long": "Longitude must be between -180 and 180."})

        return attrs

