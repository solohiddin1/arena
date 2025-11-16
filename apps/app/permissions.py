from django.auth import permissions

class TeacherPermissions(permissions.BasePermission):
    """
    Custom permission to only allow teachers to access certain views.
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and hasattr(request.user, 'teacher')