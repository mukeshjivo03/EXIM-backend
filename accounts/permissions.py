from rest_framework.permissions import BasePermission


class HasAppPermission(BasePermission):
    def __init__(self, perm: str):
        self.perm = perm

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.has_perm(self.perm)
        )