from drf_spectacular.utils import extend_schema
from rest_framework.generics import GenericAPIView

from apps.notification.api.serializers.notification import NotificationSerializer
from apps.notification.repositories.notification_repo import NotificationRepo
from apps.shared.pagination import CustomPageNumberPagination
from apps.shared.utils import SuccessResponse
from apps.users.permissions import ClientPermission


@extend_schema(tags=["notification"], summary="List user notifications")
class NotificationListView(GenericAPIView):
    permission_classes = [ClientPermission]
    serializer_class = NotificationSerializer
    pagination_class = CustomPageNumberPagination

    def get(self, request, *args, **kwargs):
        notifications = NotificationRepo.get_user_notifications(request.user)
        unread = notifications.filter(is_read=False).count()
        page = self.paginate_queryset(notifications)
        serializer = self.get_serializer(page, many=True)
        paginated = self.get_paginated_response(serializer.data)
        if isinstance(paginated, dict):
            paginated["unread_count"] = unread
        return SuccessResponse(paginated)
