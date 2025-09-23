from rest_framework.permissions import BasePermission

class IsProUser(BasePermission):
    """
    Allows access only to Pro or higher subscription users.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.subscription in ["pro", "enterprise"]


class IsEnterpriseUser(BasePermission):
    """
    Allows access only to Enterprise users.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.subscription == "enterprise"
