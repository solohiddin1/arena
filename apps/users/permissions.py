from rest_framework.permissions import BasePermission

from apps.users.models import User


class ClientPermission(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        db_user = User.objects.only('is_active', 'is_verified').filter(
            id=request.user.id,
        ).first()

        if db_user is None:
            return False

        return bool(db_user.is_active and db_user.is_verified)
