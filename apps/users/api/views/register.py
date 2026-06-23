from django.db import transaction
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework.generics import GenericAPIView

from apps.shared.enum import ResultCodes
from apps.shared.middleware.middleware import get_logger
from apps.shared.utils import ErrorResponse, SuccessResponse
from apps.users.api.serializers import RegisterSerializer
from apps.users.services.user_service import UserService

user_service = UserService()
ACCEPT_LANGUAGE_HEADER = []

logger = get_logger()

@extend_schema(
    tags=["auth-register"],
    parameters=ACCEPT_LANGUAGE_HEADER,
    summary="to register user",
)
class RegisterUser(GenericAPIView):
    serializer_class = RegisterSerializer
    filter_backends = [DjangoFilterBackend]
    role = "USER"

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            result = user_service.register_user(serializer.validated_data)
            if result.get("error"):
                return ErrorResponse(result["error"])
            return SuccessResponse(result["data"])
        except Exception as e:
            logger.error(f"Error in registration: {str(e)}")
            return ErrorResponse(ResultCodes.INTERNAL_SERVER_ERROR)