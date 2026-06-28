from rest_framework import serializers

from apps.posts.models import Feedback


class FeedbackReadSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source="user.id", read_only=True)
    user_email = serializers.CharField(source="user.email", read_only=True)
    user_full_name = serializers.CharField(source="user.full_name", read_only=True)

    class Meta:
        model = Feedback
        fields = (
            "id",
            "post",
            "user_id",
            "user_email",
            "user_full_name",
            "rating",
            "comment",
            "created_at",
            "updated_at",
        )


class FeedbackWriteSerializer(serializers.Serializer):
    post_id = serializers.IntegerField(required=True)
    rating = serializers.IntegerField(required=False, allow_null=True)
    comment = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    def validate_rating(self, value):
        if value is None:
            return value
        if value < 1 or value > 5:
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value

    def validate(self, attrs):
        rating = attrs.get("rating")
        comment = attrs.get("comment")

        if rating is None and not comment:
            raise serializers.ValidationError("At least one of rating or comment must be provided.")

        return attrs
