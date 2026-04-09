from drf_spectacular.utils import extend_schema
from rest_framework.generics import GenericAPIView

from apps.users.models import User
from apps.users.services.user_service import UserService
from apps.shared.utils import ErrorResponse, SuccessResponse
from apps.users.api.serializers import ApplyNewPasswordSerializer

user_service = UserService()


class ApplyNewPassword(GenericAPIView):
    queryset = User.objects.all()
    serializer_class = ApplyNewPasswordSerializer

    @extend_schema(tags=["password"])
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = user_service.apply_new_password(
            email=serializer.validated_data["email"],
            code=serializer.validated_data["code"],
            password=serializer.validated_data["password"],
        )
        if result.get("error"):
            return ErrorResponse(result["error"])
        return SuccessResponse(result["data"])
