from drf_spectacular.utils import extend_schema
from rest_framework.generics import GenericAPIView

from apps.shared.utils import ErrorResponse, SuccessResponse
from apps.users.api.serializers import AuthenticationSerializer
from apps.users.services.user_service import UserService

user_service = UserService()


@extend_schema(
    tags=["auth"],
    summary="login verified user with phone_number and password and return tokens",
    responses={200: AuthenticationSerializer},
)
class LoginUser(GenericAPIView):
    serializer_class = AuthenticationSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone_number = serializer.validated_data.get("phone_number") or serializer.validated_data.get("username")
        result = user_service.login_user(
            request=request,
            phone_number=phone_number,
            password=serializer.validated_data.get("password"),
        )
        if result.get("error"):
            return ErrorResponse(result["error"])
        return SuccessResponse(result["data"])
