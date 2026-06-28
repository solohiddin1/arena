import json

from rest_framework import serializers

from apps.posts.models import Amenity, Category, Post, PostImage, PostWorkDays, PostCertificate
from apps.users.api.serializers.profile import UserProfileSerializer
from apps.shared.serializers import PostRegionSerializer, PostDistrictSerializer


class AmenitySerializer(serializers.ModelSerializer):
    title = serializers.SerializerMethodField()

    class Meta:
        model = Amenity
        fields = ("id", "title", "is_positive")

    def get_title(self, obj):
        # Returns the title in the active language (set from the Accept-Language
        # header by LocaleMiddleware), falling back to any available translation.
        return obj.safe_translation_getter("title", any_language=True)


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
        fields = ("id", "post", "image", "image_compressed")


class PostCertificateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostCertificate
        fields = ("id", "image", "image_compressed")


class PostBaseSerializer(serializers.ModelSerializer):
    average_rating = serializers.SerializerMethodField()
    total_feedbacks = serializers.IntegerField(read_only=True)
    distance_km = serializers.SerializerMethodField()
    is_favourite = serializers.SerializerMethodField()
    owner = UserProfileSerializer(read_only=True)
    region = PostRegionSerializer(read_only=True)
    district = PostDistrictSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    images = serializers.SerializerMethodField()
    certificates = serializers.SerializerMethodField()
    work_days = PostWorkDaysSerializer(many=True, read_only=True)
    amenities = AmenitySerializer(many=True, read_only=True)

    class Meta:
        model = Post
        fields = (
            "id",
            "title",
            "location_title",
            "phone_number",
            "social_media_link",
            "social_media_type",
            "images",
            "certificates",
            "prices",
            "lat",
            "long",
            "state",
            "comment_count",
            "owner",
            "region",
            "district",
            "category",
            "description",
            "average_rating",
            "total_feedbacks",
            "distance_km",
            "is_favourite",
            "work_days",
            "amenities",
            "created_at",
            "updated_at",
        )

    def get_is_favourite(self, obj):
        favourite_post_ids = self.context.get("favourite_post_ids")
        if favourite_post_ids is None:
            return None
        return obj.id in favourite_post_ids

    def get_distance_km(self, obj):
        return getattr(obj, "distance_km", None)

    def get_average_rating(self, obj):
        annotated_value = getattr(obj, "avg_rating_value", None)
        if annotated_value is not None:
            return float(annotated_value)
        return obj.average_rating

    def get_images(self, obj):
        images = obj.post_images.filter(is_hidden=False)
        return PostImagesSerializer(images, many=True, context=self.context).data

    def get_certificates(self, obj):
        certificates = obj.post_certificates.filter(is_hidden=False)
        return PostCertificateSerializer(certificates, many=True, context=self.context).data


class PostListSerializer(PostBaseSerializer):
    class Meta:
        model = Post
        fields = (
            "id",
            "title",
            "location_title",
            "images",
            "prices",
            "lat",
            "long",
            "comment_count",
            "owner",
            "region",
            "district",
            "category",
            "average_rating",
            "total_feedbacks",
            "distance_km",
            "is_favourite",
            "work_days",
        )


class PostDetailSerializer(PostListSerializer):
    related_posts = serializers.SerializerMethodField()

    class Meta(PostListSerializer.Meta):
        fields = PostListSerializer.Meta.fields + ("related_posts",)

    def get_related_posts(self, obj):
        related_posts = Post.objects.filter(
            category=obj.category,
            state='ACCEPTED',
            is_hidden=False,
        ).exclude(id=obj.id).order_by('-created_at')[:5]
        return PostBaseSerializer(related_posts, many=True, context=self.context).data


class PostWriteSerializer(serializers.ModelSerializer):
    work_hours = serializers.CharField(required=False, allow_null=True, write_only=True)
    prices = serializers.CharField(required=False, allow_null=True, write_only=True)
    amenity_ids = serializers.PrimaryKeyRelatedField(
        queryset=Amenity.objects.all(),
        many=True,
        required=False,
        write_only=True,
        source="amenities",
    )

    def to_internal_value(self, data):
        if hasattr(data, 'getlist'):
            raw = data.getlist('amenity_ids')
            if len(raw) == 1 and isinstance(raw[0], str):
                value = raw[0].strip()
                if not value:
                    data = data.copy()
                    data.setlist('amenity_ids', [])
                elif value.startswith('['):
                    try:
                        parsed = json.loads(value)
                        data = data.copy()
                        data.setlist('amenity_ids', [str(i) for i in parsed])
                    except (json.JSONDecodeError, ValueError):
                        pass
                elif ',' in value:
                    data = data.copy()
                    data.setlist('amenity_ids', [i.strip() for i in value.split(',') if i.strip()])
        return super().to_internal_value(data)

    class Meta:
        model = Post
        fields = (
            "title",
            "description",
            "location_title",
            "phone_number",
            "social_media_link",
            "social_media_type",
            "prices",
            "lat",
            "long",
            "region",
            "district",
            "category",
            "work_hours",
            "amenity_ids",
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

    def validate_prices(self, value):
        if value is None:
            return None
        if isinstance(value, str):
            try:
                value = json.loads(value)
            except json.JSONDecodeError:
                raise serializers.ValidationError("Invalid JSON.")
        if not isinstance(value, list):
            raise serializers.ValidationError("Prices must be a list of objects.")
        for item in value:
            if not isinstance(item, dict) or 'name' not in item or 'value' not in item:
                raise serializers.ValidationError("Each price must have 'name' and 'value'.")
        return value

    def validate(self, attrs):
        lat = attrs.get("lat")
        long = attrs.get("long")

        if lat is not None and not (-90 <= lat <= 90):
            raise serializers.ValidationError({"lat": "Latitude must be between -90 and 90."})

        if long is not None and not (-180 <= long <= 180):
            raise serializers.ValidationError({"long": "Longitude must be between -180 and 180."})

        return attrs

