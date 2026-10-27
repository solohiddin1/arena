import math

from django.db.models import Avg, Q, QuerySet
from apps.users.models import User
from apps.posts.models import Amenity, Category, Feedback, Post, PostImage, PostWorkDays, PostCertificate


class PostService:

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

    def get_post(self, post_id: int, include_hidden: bool = False, user_lat: float = None, user_long: float = None) -> Post | None:
        queryset = (
            Post.objects.filter(state="ACCEPTED")
            .select_related("owner", "region", "district", "category")
            .prefetch_related("work_days", "amenities")
            .filter(id=post_id)
        )
        if not include_hidden:
            queryset = queryset.filter(is_hidden=False)
        post = queryset.first()
        if post and user_lat is not None and user_long is not None and post.lat is not None and post.long is not None:
            post.distance_km = round(self._distance_km(user_lat, user_long, post.lat, post.long), 2)
        return post

    def get_my_post(self, post_id: int, user: User, include_hidden: bool = False) -> Post | None:
        queryset = (
            Post.objects.filter(owner=user)
            .select_related("owner", "region", "district", "category")
            .prefetch_related("work_days", "amenities")
            .filter(id=post_id)
        )
        if not include_hidden:
            queryset = queryset.filter(is_hidden=False)
        return queryset.first()

    def list_my_posts(self, user, include_hidden: bool = False):
        queryset = (
            Post.objects.select_related("owner", "region", "district", "category")
            .prefetch_related("work_days", "amenities")
            .filter(owner=user)
            .annotate(avg_rating_value=Avg("post_feedbacks__rating"))
            .order_by("-created_at")
        )
        if not include_hidden:
            queryset = queryset.filter(is_hidden=False)
        return queryset

    def list_posts(self, filters: dict):
        queryset = (
            Post.objects.filter(state="ACCEPTED", is_hidden=False)
            .select_related("owner", "region", "district", "category")
            .prefetch_related("work_days", "amenities")
            .annotate(avg_rating_value=Avg("post_feedbacks__rating"))
        )

        owner_id = filters.get("owner")
        state = filters.get("state")
        region_id = filters.get("region")
        district_id = filters.get("district")
        category_id = filters.get("category")
        category_ids = self._to_int_list(filters.get("category_ids"))
        min_cost = filters.get("min_cost")
        max_cost = filters.get("max_cost")
        search = filters.get("search")
        user_lat = self._to_float(filters.get("lat"))
        user_long = self._to_float(filters.get("long"))

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
        if search:
            queryset = queryset.filter(title__icontains=search)

        queryset = queryset.order_by("-created_at")

        min_cost_val = int(min_cost) if min_cost is not None and min_cost != "" else None
        max_cost_val = int(max_cost) if max_cost is not None and max_cost != "" else None

        def matches_cost(post):
            if min_cost_val is None and max_cost_val is None:
                return True
            prices = post.prices or []
            values = [p.get("value") for p in prices if isinstance(p, dict) and p.get("value") is not None]
            if not values:
                return True
            if min_cost_val is not None and max_cost_val is not None:
                return any(min_cost_val <= v <= max_cost_val for v in values)
            if min_cost_val is not None:
                return any(v >= min_cost_val for v in values)
            return any(v <= max_cost_val for v in values)

        if user_lat is None or user_long is None:
            if min_cost_val is not None or max_cost_val is not None:
                return [p for p in queryset if matches_cost(p)]
            return queryset

        posts_with_distance = []
        for post in queryset.exclude(lat__isnull=True, long__isnull=True):
            if not matches_cost(post):
                continue
            post.distance_km = round(self._distance_km(user_lat, user_long, post.lat, post.long), 2)
            posts_with_distance.append(post)

        posts_with_distance.sort(key=lambda p: p.distance_km)
        return posts_with_distance

    def _process_amenities(self, amenities_data: list, post: Post | None = None) -> list[Amenity]:
        if not amenities_data:
            return []

        result_amenities = []
        seen_ids = set()

        for item in amenities_data:
            if isinstance(item, (int, str)):
                s = str(item).strip()
                if s.isdigit():
                    item = {"id": int(s)}
                else:
                    item = {"title": s, "is_positive": True}

            if not isinstance(item, dict):
                continue

            amenity_id = item.get("id")
            title = item.get("title") or item.get("name")
            is_positive = item.get("is_positive", True)

            if amenity_id:
                amenity = Amenity.objects.filter(id=amenity_id).first()
                if not amenity:
                    continue

                updated = False
                if "is_positive" in item and amenity.is_positive != bool(is_positive):
                    amenity.is_positive = bool(is_positive)
                    updated = True

                if title:
                    title_str = str(title).strip()
                    # If user is updating a custom amenity (non-main system amenity)
                    if not amenity.is_main:
                        amenity.title = title_str
                        amenity.title_uz = title_str
                        amenity.title_ru = title_str
                        amenity.title_en = title_str
                        updated = True

                if updated:
                    amenity.save()

                if amenity.id not in seen_ids:
                    seen_ids.add(amenity.id)
                    result_amenities.append(amenity)

            elif title:
                title_str = str(title).strip()
                if not title_str:
                    continue
                # Custom amenity created on the fly
                amenity = Amenity.objects.filter(
                    Q(title__iexact=title_str)
                    | Q(title_uz__iexact=title_str)
                    | Q(title_ru__iexact=title_str)
                    | Q(title_en__iexact=title_str)
                ).first()
                if not amenity:
                    amenity = Amenity.objects.create(
                        title=title_str,
                        title_uz=title_str,
                        title_ru=title_str,
                        title_en=title_str,
                        is_positive=bool(is_positive),
                        is_main=False,
                    )
                else:
                    if "is_positive" in item and amenity.is_positive != bool(is_positive):
                        amenity.is_positive = bool(is_positive)
                        amenity.save()

                if amenity.id not in seen_ids:
                    seen_ids.add(amenity.id)
                    result_amenities.append(amenity)

        return result_amenities

    def create_post(self, owner, validated_data: dict) -> Post:
        work_hours = validated_data.pop("work_hours", None)
        amenities_data = validated_data.pop("amenities", None) or []
        amenity_ids = validated_data.pop("amenity_ids", None)
        custom_amenities = validated_data.pop("custom_amenities", None)

        post = Post.objects.create(owner=owner, **validated_data)
        if work_hours:
            self._create_work_days(post, work_hours)

        if amenity_ids:
            amenities_data.extend([{"id": i} for i in amenity_ids])
        if custom_amenities:
            amenities_data.extend([{"title": c, "is_positive": True} for c in custom_amenities])

        if amenities_data:
            resolved = self._process_amenities(amenities_data, post=post)
            post.amenities.set(resolved)
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

    def create_post_certificates(self, post: Post, certificate_files) -> None:
        if not certificate_files:
            return
        PostCertificate.objects.bulk_create([PostCertificate(post=post, image=cert_file) for cert_file in certificate_files])

    def remove_post_images(self, post: Post, image_ids: list) -> list:
        """Soft-delete images. Returns list of invalid IDs (not owned by this post)."""
        if not image_ids:
            return []
        owned = set(PostImage.objects.filter(post=post, id__in=image_ids).values_list("id", flat=True))
        invalid = [i for i in image_ids if i not in owned]
        if invalid:
            return invalid
        PostImage.objects.filter(id__in=image_ids).update(is_hidden=True)
        return []

    def remove_post_certificates(self, post: Post, cert_ids: list) -> list:
        """Soft-delete certificates. Returns list of invalid IDs (not owned by this post)."""
        if not cert_ids:
            return []
        owned = set(PostCertificate.objects.filter(post=post, id__in=cert_ids).values_list("id", flat=True))
        invalid = [i for i in cert_ids if i not in owned]
        if invalid:
            return invalid
        PostCertificate.objects.filter(id__in=cert_ids).update(is_hidden=True)
        return []

    def update_post(self, post: Post, validated_data: dict) -> Post:
        work_hours = validated_data.pop("work_hours", None)
        has_amenities = (
            "amenities" in validated_data
            or "amenity_ids" in validated_data
            or "custom_amenities" in validated_data
        )
        amenities_data = validated_data.pop("amenities", None)
        amenity_ids = validated_data.pop("amenity_ids", None)
        custom_amenities = validated_data.pop("custom_amenities", None)

        for attr, value in validated_data.items():
            setattr(post, attr, value)
        post.save()

        if work_hours is not None:
            post.work_days.all().delete()
            self._create_work_days(post, work_hours)

        if has_amenities:
            merged = []
            if amenities_data is not None:
                merged.extend(amenities_data)
            if amenity_ids:
                merged.extend([{"id": i} for i in amenity_ids])
            if custom_amenities:
                merged.extend([{"title": c, "is_positive": True} for c in custom_amenities])

            resolved = self._process_amenities(merged, post=post)
            post.amenities.set(resolved)

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
        }
        feedback, _ = Feedback.objects.update_or_create(
            user=user,
            post=post,
            defaults=defaults,
        )
        return feedback

    def list_categories(self) -> QuerySet[Category]:
        return Category.objects.all().order_by("ordering", "id")

    def list_amenities(
        self,
        is_positive: bool | None = None,
        is_main: bool | None = True,
        category_id: int | None = None,
    ) -> QuerySet[Amenity]:
        queryset = Amenity.objects.all().order_by("id")
        if is_positive is not None:
            queryset = queryset.filter(is_positive=is_positive)
        if is_main is not None:
            queryset = queryset.filter(is_main=is_main)
        if category_id is not None:
            queryset = queryset.filter(category_id=category_id)
        return queryset
