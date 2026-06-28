from rest_framework import serializers

from apps.posts.models import AppFeedback


class AppFeedbackReadSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source="user.id", read_only=True, allow_null=True)
    user_email = serializers.CharField(source="user.email", read_only=True, allow_null=True)

    class Meta:
        model = AppFeedback
        fields = ("id", "user_id", "user_email", "message", "rating", "created_at")


class AppFeedbackWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppFeedback
        fields = ("message", "rating")

    def validate_rating(self, value):
        if value is not None and not (1 <= value <= 5):
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value