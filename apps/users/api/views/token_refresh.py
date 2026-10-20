from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.views import TokenRefreshView

from apps.shared.utils import SuccessResponse
from apps.users.api.serializers.auth import RefreshTokenSerializer


@extend_schema(
    tags=["auth"],
    summary="Refresh JWT access and refresh tokens",
    request=RefreshTokenSerializer,
    responses={200: RefreshTokenSerializer},
)
class CustomTokenRefreshView(TokenRefreshView):
    permission_classes = [AllowAny]
    serializer_class = RefreshTokenSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])

        return SuccessResponse(serializer.validated_data, status=status.HTTP_200_OK)
