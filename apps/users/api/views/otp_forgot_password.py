from drf_spectacular.utils import extend_schema
from rest_framework.generics import GenericAPIView

from apps.shared.utils import ErrorResponse, SuccessResponse
from apps.users.api.serializers import OtpForgotPasswordSerializer
from apps.users.models import User
from apps.users.services.user_service import UserService

user_service = UserService()


class OtpForgotPassword(GenericAPIView):
    queryset = User.objects.all()
    serializer_class = OtpForgotPasswordSerializer

    @extend_schema(tags=["password"])
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = user_service.request_forgot_password_otp(serializer.validated_data["email"])
        if result.get("error"):
            return ErrorResponse(result["error"])
        return SuccessResponse(result["data"])
