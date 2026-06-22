import math

from django.db.models import Avg, QuerySet

from apps.posts.models import Amenity, Category, Feedback, Post, PostImage, PostWorkDays


class PostService:
    DEFAULT_RADIUS_KM = 10.0

    @staticmethod
    def _to_float(value):
        try:
            if value is None or value == "":
                return None
            return float(value)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _to_int_list(value):
        if not value:
            return []
        if isinstance(value, (list, tuple)):
            raw_values = value
        else:
            raw_values = str(value).split(",")

        result = []
        for item in raw_values:
            try:
                cleaned = str(item).strip()
                if cleaned:
                    result.append(int(cleaned))
            except (TypeError, ValueError):
                continue
        return result

    @staticmethod
    def _distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)

        delta_lat = lat2_rad - lat1_rad
        delta_lon = lon2_rad - lon1_rad

        a = (
            math.sin(delta_lat / 2) ** 2
            + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2
        )
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        return 6371.0 * c

    def get_post(self, post_id: int, include_hidden: bool = False) -> Post | None:
        queryset = (
            Post.objects.filter(state="ACCEPTED")
            .select_related("owner", "region", "district", "category")
            .prefetch_related("work_days", "amenities__translations")
            .filter(id=post_id)
        )
        if not include_hidden:
            queryset = queryset.filter(is_hidden=False)
        return queryset.first()

    def list_my_posts(self, user, include_hidden: bool = False):
        queryset = (
            Post.objects.select_related("owner", "region", "district", "category")
            .prefetch_related("work_days", "amenities__translations")
            .filter(owner=user)
            .annotate(avg_rating_value=Avg("post_feedbacks__rating"))
            .order_by("-created_at")
        )
        if not include_hidden:
            queryset = queryset.filter(is_hidden=False)
        return queryset

    def list_posts(self, filters: dict):
        queryset = Post.objects.select_related("owner", "region", "district", "category").prefetch_related("work_days", "amenities__translations").filter(
            is_hidden=False
        ).annotate(
            avg_rating_value=Avg("post_feedbacks__rating")
        )

        owner_id = filters.get("owner")
        state = filters.get("state")
        region_id = filters.get("region")
        district_id = filters.get("district")
        category_id = filters.get("category")
        category_ids = self._to_int_list(filters.get("category_ids"))
        min_rating = self._to_float(filters.get("rating"))
        min_cost = filters.get("min_cost")
        max_cost = filters.get("max_cost")
        search = filters.get("search")
        user_lat = self._to_float(filters.get("lat"))
        user_long = self._to_float(filters.get("long"))
        radius_km = self._to_float(filters.get("radius_km")) or self.DEFAULT_RADIUS_KM

        if owner_id:
            queryset = queryset.filter(owner_id=owner_id)
        if state:
            queryset = queryset.filter(state=state)
        if region_id:
            queryset = queryset.filter(region_id=region_id)
        if district_id:
            queryset = queryset.filter(district_id=district_id)
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        if category_ids:
            queryset = queryset.filter(category_id__in=category_ids)
        if min_rating is not None:
            queryset = queryset.filter(avg_rating_value__gte=min_rating)
        if min_cost:
            queryset = queryset.filter(prices__contains=[{'value': min_cost}]) # Note: This might not work perfectly with JSONField for GT/LT
        if max_cost:
            queryset = queryset.filter(prices__contains=[{'value': max_cost}])
        if search:
            queryset = queryset.filter(title__icontains=search)

        queryset = queryset.order_by("-created_at")

        if user_lat is None or user_long is None:
            return queryset

        nearby_posts = []
        for post in queryset.exclude(lat__isnull=True, long__isnull=True):
            distance_km = self._distance_km(user_lat, user_long, post.lat, post.long)
            if distance_km <= radius_km:
                post.distance_km = round(distance_km, 2)
                nearby_posts.append(post)

        nearby_posts.sort(key=lambda item: item.distance_km)
        return nearby_posts

    def create_post(self, owner, validated_data: dict) -> Post:
        work_hours = validated_data.pop("work_hours", None)
        amenities = validated_data.pop("amenities", [])
        post = Post.objects.create(owner=owner, **validated_data)
        if work_hours:
            self._create_work_days(post, work_hours)
        if amenities:
            post.amenities.set(amenities)
        return post

    def _create_work_days(self, post: Post, work_hours: list) -> None:
        entries = []
        for group in work_hours:
            days = group["days"]
            for day in days:
                entries.append(PostWorkDays(
                    post=post,
                    day_of_week=day,
                    start_time=group.get("start_time"),
                    end_time=group.get("end_time"),
                    is_closed=group.get("is_closed", False),
                    is_full_time=group.get("is_full_time", False),
                ))
        PostWorkDays.objects.bulk_create(entries)

    def create_post_images(self, post: Post, image_files) -> None:
        if not image_files:
            return
        PostImage.objects.bulk_create([PostImage(post=post, image=image_file) for image_file in image_files])

    def update_post(self, post: Post, validated_data: dict) -> Post:
        work_hours = validated_data.pop("work_hours", None)
        amenities = validated_data.pop("amenities", None)
        for attr, value in validated_data.items():
            setattr(post, attr, value)
        post.save()
        if work_hours is not None:
            post.work_days.all().delete()
            self._create_work_days(post, work_hours)
        if amenities is not None:
            post.amenities.set(amenities)
        return post

    def delete_post(self, post: Post) -> None:
        post.is_hidden = True
        post.save(update_fields=["is_hidden", "updated_at"])

    def list_feedbacks(self, post: Post) -> QuerySet[Feedback]:
        return Feedback.objects.select_related("user", "post").filter(post=post).order_by("-created_at")

    def upsert_feedback(self, user, post: Post, validated_data: dict) -> Feedback:
        defaults = {
            "rating": validated_data.get("rating"),
            "comment": validated_data.get("comment"),
            "name": validated_data.get("name"),
        }
        feedback, _ = Feedback.objects.update_or_create(
            user=user,
            post=post,
            defaults=defaults,
        )
        return feedback

    def list_categories(self) -> QuerySet[Category]:
        return Category.objects.all().order_by("title")

    def list_amenities(self, is_positive: bool | None = None) -> QuerySet[Amenity]:
        queryset = Amenity.objects.prefetch_related("translations").order_by("id")
        if is_positive is not None:
            queryset = queryset.filter(is_positive=is_positive)
        return queryset
