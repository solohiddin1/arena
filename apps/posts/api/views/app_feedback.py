from drf_spectacular.utils import extend_schema
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAdminUser

from apps.posts.api.serializers.app_feedback import AppFeedbackReadSerializer, AppFeedbackWriteSerializer
from apps.posts.models import AppFeedback
from apps.shared.utils import SuccessResponse
from apps.users.permissions import ClientPermission


@extend_schema(tags=["app-feedback"], summary="List app feedbacks")
class AppFeedbackListView(GenericAPIView):
    permission_classes = [ClientPermission]
    serializer_class = AppFeedbackReadSerializer

    def get(self, request, *args, **kwargs):
        feedbacks = AppFeedback.objects.filter(user=request.user)
        serializer = self.get_serializer(feedbacks, many=True)
        return SuccessResponse(serializer.data)


@extend_schema(tags=["app-feedback"], summary="Submit app feedback")
class AppFeedbackCreateView(GenericAPIView):
    permission_classes = [ClientPermission]
    serializer_class = AppFeedbackWriteSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return SuccessResponse({"detail": "Thank you for your feedback!"})