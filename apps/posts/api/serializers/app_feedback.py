from rest_framework import serializers

from apps.posts.models import AppFeedback


class AppFeedbackWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppFeedback
        fields = ("message", "rating")

    def validate_rating(self, value):
        if value is not None and not (1 <= value <= 5):
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value