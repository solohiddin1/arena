from drf_spectacular.utils import extend_schema
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated

from apps.shared.enum import ResultCodes
from apps.shared.utils import error_response, success_response
from apps.users.api.serializers.set_password import SetPasswordSerializer
from apps.users.services.user_service import UserService

user_service = UserService()


@extend_schema(
    tags=["auth"],
    summary="Set new password for authenticated user (after Telegram login / in app)",
    request=SetPasswordSerializer,
)
class SetPasswordView(GenericAPIView):
    serializer_class = SetPasswordSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        password = serializer.validated_data.get("password")
        return user_service.set_user_password(request.user, password)
