from drf_spectacular.utils import extend_schema
from rest_framework.generics import GenericAPIView

from apps.shared.utils import SuccessResponse
from apps.users.api.serializers import CheckRegisterSerializer
from apps.users.repository import get_user_by_username


@extend_schema(
    tags=["auth"],
    summary="check if user already exists by email",
)
class CheckRegister(GenericAPIView):
    serializer_class = CheckRegisterSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = get_user_by_username(serializer.validated_data["email"])
        return SuccessResponse({"exists": bool(user)})
