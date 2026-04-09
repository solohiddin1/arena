from drf_spectacular.utils import extend_schema
from rest_framework import generics
from rest_framework.parsers import MultiPartParser

from apps.shared.enum import ResultCodes
from apps.shared.utils import ErrorResponse, SuccessResponse
from apps.users.api.serializers import UserProfileImageUpdateSerializer
from apps.users.models import User
from apps.users.permissions import ClientPermission


class UserUpdateProfileImage(generics.UpdateAPIView):
    queryset = User.objects.all()
    permission_classes = [ClientPermission]
    serializer_class = UserProfileImageUpdateSerializer
    parser_classes = [MultiPartParser]
    http_method_names = ["patch"]

    @extend_schema(
        tags=["user-profile"],
        request={
            "multipart/form-data": {
                "type": "object",
                "properties": {
                    "image": {"type": "string", "format": "binary"}
                },
            }
        }
    )
    def patch(self, request, *args, **kwargs):
        user = request.user
        serializer = UserProfileImageUpdateSerializer(user, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return SuccessResponse({"message": "Image updated"})

        return ErrorResponse(ResultCodes.UNKNOWN_ERROR)
