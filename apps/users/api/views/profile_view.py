from drf_spectacular.utils import extend_schema
from rest_framework.generics import GenericAPIView

from apps.shared.utils import SuccessResponse
from apps.users.api.serializers import UserProfileSerializer
from apps.users.permissions import ClientPermission


@extend_schema(
    tags=["user-profile"],
    summary="Get authenticated user profile",
)
class UserProfileView(GenericAPIView):
    permission_classes = [ClientPermission]

    def get(self, request, *args, **kwargs):
        return SuccessResponse(UserProfileSerializer(request.user, context={"request": request}).data)
