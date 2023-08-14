from rest_framework.permissions import (
    BasePermission,
    SAFE_METHODS,
)


class IsAdminOrIfAuthenticatedReadOnly(BasePermission):

    def has_permission(self, request, view):

        return (
            (
                request.method in SAFE_METHODS
                and request.user
            )
            or (request.user.is_authenticated and request.user.is_staff)
        )
