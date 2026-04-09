from django.db import transaction
from drf_spectacular.utils import extend_schema
from rest_framework.generics import GenericAPIView

from apps.shared.utils import ErrorResponse, SuccessResponse
from apps.users.api.serializers import UserVerifySerializer
from apps.users.services.user_service import UserService

user_service = UserService()


@extend_schema(
    tags=["auth-register"],
    summary="to verify registered user, send users id and otp , user id is " \
    "returned when they are  registered",
)
class VerifyOtp(GenericAPIView):
    serializer_class = UserVerifySerializer

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = user_service.verify_registration_otp(
            user_id=serializer.validated_data["user_id"],
            code=serializer.validated_data["code"],
        )
        if result.get("error"):
            return ErrorResponse(result["error"])
        return SuccessResponse(result["data"])
