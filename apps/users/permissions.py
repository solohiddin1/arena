from rest_framework.permissions import BasePermission

from apps.users.models import UserRole


class ClientPermission(BasePermission):
    def has_permission(self, request, view):
        if request.auth is None:
            return False

        if request.auth.get("role") != "USER":
            return False

        # Only fetch required fields - don't need user object here
        db_role = UserRole.objects.only('is_active', 'is_verified').filter(
            user=request.user,
            role="USER"
        ).first()

        if db_role is None:
            return False

        return bool(request.user and db_role.is_active and db_role.is_verified)


class SellerPermission(BasePermission):
    def has_permission(self, request, view):
        if request.auth is None:
            return False

        if request.auth.get("role") != "SELLER":
            return False

        # Only fetch required fields - don't need user object here
        db_role = UserRole.objects.only('is_active', 'is_verified').filter(
            user=request.user,
            role="SELLER"
        ).first()

        if db_role is None:
            return False

        return bool(request.user and db_role.is_active and db_role.is_verified)


class AdminPermission(BasePermission):
    def has_permission(self, request, view):
        if request.auth is None:
            return False

        if request.auth.get("role") != "ADMIN":
            return False

        # Only fetch required fields - don't need user object here
        db_role = UserRole.objects.only('is_active', 'is_verified').filter(
            user=request.user,
            role="ADMIN"
        ).first()

        if db_role is None:
            return False

        return bool(request.user and db_role.is_active and db_role.is_verified)