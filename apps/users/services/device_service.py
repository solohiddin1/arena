from apps.shared.enum import ResultCodes
from apps.shared.utils import error_response, success_response
from apps.users.api.serializers.device_add import DeviceSerializer
from apps.users.models import User
from apps.users.repositories.device_repo import DeviceRepo


class DeviceService:
    @staticmethod
    def add_device(
        user: User, name: str, device_type: str, device_id: str, fcm_token: str = ""
    ):
        device = DeviceRepo.add_device(user, name, device_type, device_id, fcm_token)
        return success_response(DeviceSerializer(device).data)

    @staticmethod
    def delete_device(user: User, device_id):
        device = None
        try:
            device_id_int = int(device_id)
            device = DeviceRepo.get_active_by_id(device_id_int, user)
        except (ValueError, TypeError):
            device = None

        if device is None:
            device = DeviceRepo.get_active_by_device_id(str(device_id), user)

        if device is None:
            return error_response(ResultCodes.DEVICE_NOT_FOUND)
        DeviceRepo.deactivate(device)
        return success_response({"detail": "Device deleted successfully."})

    @staticmethod
    def deactivate_by_device_id(user: User, device_id: str) -> None:
        device = DeviceRepo.get_active_by_device_id(device_id, user)
        if device is not None:
            DeviceRepo.deactivate(device)
