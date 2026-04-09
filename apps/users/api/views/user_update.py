from drf_spectacular.utils import extend_schema
from rest_framework import generics

from apps.shared.utils import SuccessResponse
from apps.users.api.serializers import UserUpdateSerializer
from apps.users.models import User
from apps.users.permissions import ClientPermission


class UserUpdate(generics.UpdateAPIView):
    queryset = User.objects.all()
    permission_classes = [ClientPermission]
    serializer_class = UserUpdateSerializer
    http_method_names = ["patch"]

    def get_object(self):
        return self.request.user

    @extend_schema(tags=["user-profile"])
    def partial_update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, "_prefetched_objects_cache", None):
            instance._prefetched_objects_cache = {}

        return SuccessResponse(serializer.data)
