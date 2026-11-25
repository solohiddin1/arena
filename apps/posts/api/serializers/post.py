import json

from rest_framework import serializers

from apps.posts.models import Amenity, Category, Post, PostImage, PostWorkDays, PostCertificate, PostSocialMedia
from apps.users.api.serializers.profile import UserProfileSerializer
from apps.shared.serializers import PostRegionSerializer, PostDistrictSerializer


class AmenitySerializer(serializers.ModelSerializer):
    main = serializers.BooleanField(source="is_main", read_only=True)

    class Meta:
        model = Amenity
        fields = ("id", "title", "title_uz", "title_ru", "title_en", "is_positive", "is_main", "main", "category")


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("id", "title", "title_uz", "title_ru", "title_en", "image", "ordering")


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


class PostSocialMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostSocialMedia
        fields = ("id", "type", "link")


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
    social_media_links = PostSocialMediaSerializer(source="social_links", many=True, read_only=True)

    class Meta:
        model = Post
        fields = (
            "id",
            "title",
            "location_title",
            "phone_number",
            "social_media_links",
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
        fields = PostListSerializer.Meta.fields + (
            "related_posts",
            "description",
            "phone_number",
            "social_media_links",
            "certificates",
            "state",
            "amenities",
            "created_at",
            "updated_at",
        )

    def get_related_posts(self, obj):
        related_posts = Post.objects.filter(
            category=obj.category,
            state='ACCEPTED',
            is_hidden=False,
        ).exclude(id=obj.id).order_by('-created_at')[:5]
        return PostBaseSerializer(related_posts, many=True, context=self.context).data


class PostWriteSerializer(serializers.ModelSerializer):
    work_hours = serializers.JSONField(required=False, allow_null=True, write_only=True)
    prices = serializers.JSONField(required=False, allow_null=True, write_only=True)
    amenities = serializers.JSONField(required=False, write_only=True)
    social_media_links = serializers.JSONField(required=False, write_only=True)
    custom_amenities = serializers.ListField(
        child=serializers.CharField(max_length=100),
        required=False,
        write_only=True,
    )
    amenity_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        write_only=True,
    )

    def to_internal_value(self, data):
        # Convert QueryDict to plain dict so JSONField does not treat Python objects as HTML form inputs
        if hasattr(data, "getlist"):
            plain = {}
            for key in data.keys():
                if key in ("amenity_ids", "custom_amenities"):
                    plain[key] = data.getlist(key)
                else:
                    plain[key] = data.get(key)
            data = plain
        else:
            data = data.copy() if hasattr(data, "copy") else dict(data)

        # Parse JSON string values if any of the JSON fields were passed as strings (e.g. from multipart form)
        for field in ("amenities", "social_media_links", "prices", "work_hours"):
            val = data.get(field)
            if isinstance(val, str):
                sval = val.strip()
                if not sval:
                    data[field] = []
                elif sval.startswith("[") or sval.startswith("{"):
                    try:
                        data[field] = json.loads(sval)
                    except (json.JSONDecodeError, ValueError):
                        pass

        # Handle amenity_ids if passed as a string or list of strings
        raw_ids = data.get("amenity_ids")
        if isinstance(raw_ids, str):
            val = raw_ids.strip()
            if not val:
                data["amenity_ids"] = []
            elif val.startswith("["):
                try:
                    data["amenity_ids"] = [int(i) for i in json.loads(val)]
                except (json.JSONDecodeError, ValueError):
                    pass
            elif "," in val:
                data["amenity_ids"] = [int(i.strip()) for i in val.split(",") if i.strip().isdigit()]
        elif isinstance(raw_ids, list):
            parsed_ids = []
            for item in raw_ids:
                if isinstance(item, str):
                    val = item.strip()
                    if val.startswith("["):
                        try:
                            parsed_ids.extend([int(i) for i in json.loads(val)])
                        except Exception:
                            pass
                    elif "," in val:
                        parsed_ids.extend([int(i.strip()) for i in val.split(",") if i.strip().isdigit()])
                    elif val.isdigit():
                        parsed_ids.append(int(val))
                elif isinstance(item, int):
                    parsed_ids.append(item)
            data["amenity_ids"] = parsed_ids

        # Handle custom_amenities if passed as a string or list of strings
        raw_custom = data.get("custom_amenities")
        if isinstance(raw_custom, str):
            val = raw_custom.strip()
            if not val:
                data["custom_amenities"] = []
            elif val.startswith("["):
                try:
                    data["custom_amenities"] = [str(i) for i in json.loads(val)]
                except (json.JSONDecodeError, ValueError):
                    pass
            elif "," in val:
                data["custom_amenities"] = [i.strip() for i in val.split(",") if i.strip()]
        elif isinstance(raw_custom, list):
            parsed_custom = []
            for item in raw_custom:
                if isinstance(item, str):
                    val = item.strip()
                    if val.startswith("["):
                        try:
                            parsed_custom.extend([str(i) for i in json.loads(val)])
                        except Exception:
                            pass
                    elif "," in val:
                        parsed_custom.extend([i.strip() for i in val.split(",") if i.strip()])
                    elif val:
                        parsed_custom.append(val)
                else:
                    parsed_custom.append(str(item))
            data["custom_amenities"] = parsed_custom

        return super().to_internal_value(data)

    class Meta:
        model = Post
        fields = (
            "title",
            "description",
            "location_title",
            "phone_number",
            "social_media_links",
            "prices",
            "lat",
            "long",
            "region",
            "district",
            "category",
            "work_hours",
            "amenities",
            "amenity_ids",
            "custom_amenities",
        )

    def validate_social_media_links(self, value):
        if value is None:
            return None
        if isinstance(value, str):
            val = value.strip()
            if not val:
                return []
            try:
                value = json.loads(val)
            except json.JSONDecodeError:
                raise serializers.ValidationError("Invalid JSON for social_media_links.")
        if not isinstance(value, list):
            raise serializers.ValidationError("social_media_links must be a list of objects.")

        valid_types = {t[0] for t in PostSocialMedia.SOCIAL_TYPES}
        cleaned = []
        for item in value:
            if not isinstance(item, dict):
                raise serializers.ValidationError("Each social media item must be an object with 'link' and optional 'type'.")
            link = str(item.get("link", "")).strip()
            if not link:
                continue
            stype = str(item.get("type", "OTHER")).strip().upper()
            if stype not in valid_types:
                stype = "OTHER"
            cleaned.append({"link": link, "type": stype})
        return cleaned

    def validate_amenities(self, value):
        if value is None:
            return None
        if isinstance(value, str):
            val = value.strip()
            if not val:
                return []
            try:
                value = json.loads(val)
            except json.JSONDecodeError:
                raise serializers.ValidationError("Invalid JSON for amenities.")
        if not isinstance(value, list):
            raise serializers.ValidationError("Amenities must be a list.")

        cleaned = []
        for item in value:
            if isinstance(item, int):
                cleaned.append({"id": item})
            elif isinstance(item, str):
                s = item.strip()
                if not s:
                    continue
                if s.isdigit():
                    cleaned.append({"id": int(s)})
                else:
                    cleaned.append({"title": s, "is_positive": True})
            elif isinstance(item, dict):
                amenity_id = item.get("id")
                title = item.get("title") or item.get("name")
                is_positive = item.get("is_positive", True)
                entry = {}
                if amenity_id is not None:
                    try:
                        entry["id"] = int(amenity_id)
                    except (ValueError, TypeError):
                        raise serializers.ValidationError(f"Invalid amenity id: {amenity_id}")
                if title:
                    entry["title"] = str(title).strip()
                if "is_positive" in item:
                    entry["is_positive"] = bool(is_positive)
                if not entry.get("id") and not entry.get("title"):
                    continue
                cleaned.append(entry)
            else:
                raise serializers.ValidationError("Each amenity item must be an ID, string, or object.")
        return cleaned

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