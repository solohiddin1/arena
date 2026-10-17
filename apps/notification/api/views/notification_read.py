from drf_spectacular.utils import extend_schema
from rest_framework.generics import GenericAPIView

from apps.notification.api.serializers.notification import NotificationReadSerializer
from apps.notification.models import Notification
from apps.notification.services.notification_service import NotificationService
from apps.shared.enum import ResultCodes
from apps.shared.utils import error_response
from apps.users.permissions import ClientPermission


@extend_schema(
    tags=["notification"],
    summary="Mark notification(s) as read",
    description="If 'id' or 'notification_id' is provided, marks that notification as read. If not provided or empty, marks all notifications of the user as read.",
    request=NotificationReadSerializer,
)
class NotificationReadView(GenericAPIView):
    permission_classes = [ClientPermission]
    serializer_class = NotificationReadSerializer
    queryset = Notification.objects.all()

    def post(self, request, *args, **kwargs):
        notification_id = (
            kwargs.get("notification_id")
            or request.data.get("id")
            or request.data.get("notification_id")
            or request.query_params.get("id")
            or request.query_params.get("notification_id")
        )

        if notification_id:
            try:
                notification_id = int(notification_id)
            except (ValueError, TypeError):
                return error_response(ResultCodes.INVALID_REQUEST)
            return NotificationService.mark_as_read(request.user, notification_id)

        return NotificationService.read_all(request.user)
