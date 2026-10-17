from rest_framework import serializers

from apps.notification.models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = [
            "id",
            "title",
            "body",
            "notification_type",
            "data",
            "image",
            "is_read",
            "created_at",
        ]


class NotificationReadSerializer(serializers.Serializer):
    id = serializers.IntegerField(
        required=False,
        allow_null=True,
        help_text="Notification ID to mark as read. If omitted or null, marks all notifications as read.",
    )
    notification_id = serializers.IntegerField(
        required=False,
        allow_null=True,
        help_text="Alias for id.",
    )
