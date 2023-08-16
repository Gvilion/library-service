from rest_framework.permissions import BasePermission


class IsAdminOrIfAuthenticatedReadCreateOnly(BasePermission):
    def has_permission(self, request, view):
        return bool(
            (
                request.method in ("GET", "POST", "HEAD", "OPTIONS")
                and request.user
                and request.user.is_authenticated
            )
            or (request.user and request.user.is_staff)
        )
