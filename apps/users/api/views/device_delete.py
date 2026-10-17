from drf_spectacular.utils import extend_schema
from rest_framework.generics import GenericAPIView

from apps.users.permissions import ClientPermission
from apps.users.models import Device
from apps.users.services.device_service import DeviceService


@extend_schema(
    tags=["device"],
    summary="Delete / deactivate user device",
)
class DeviceDeleteView(GenericAPIView):
    permission_classes = [ClientPermission]
    queryset = Device.objects.all()

    def delete(self, request, *args, **kwargs):
        device_id = kwargs.get("device_id")
        return DeviceService.delete_device(request.user, device_id)
