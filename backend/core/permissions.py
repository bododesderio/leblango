# backend/core/permissions.py

from rest_framework.permissions import BasePermission, SAFE_METHODS
from rest_framework import permissions

MANAGER_GROUP = "manager"
EDITOR_GROUP = "editor"


def _in_group(user, group_name: str) -> bool:
    """
    Return True if the authenticated user is in the given Django Group.
    """
    if not user or not user.is_authenticated:
        return False
    return user.groups.filter(name=group_name).exists()


class IsAuthenticatedOrReadOnly(BasePermission):
    """
    Read-only for everyone, write for authenticated users.
    """

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_authenticated)


class IsManagerOrAdmin(BasePermission):
    """
    Used for sensitive admin/analytics/query-health endpoints.

    Allows:
    - superuser
    - staff
    - users in "manager" group
    """

    def has_permission(self, request, view):
        user = request.user
        if not (user and user.is_authenticated):
            return False

        if user.is_superuser or user.is_staff:
            return True

        return _in_group(user, MANAGER_GROUP)


class IsModeratorOrAdmin(BasePermission):
    """
    For moderation endpoints (e.g. library approvals):

    Allows:
    - superuser
    - staff
    - users in "manager" or "editor" groups
    """

    def has_permission(self, request, view):
        user = request.user
        if not (user and user.is_authenticated):
            return False

        if user.is_superuser or user.is_staff:
            return True

        return _in_group(user, MANAGER_GROUP) or _in_group(user, EDITOR_GROUP)


class IsStaffUser(permissions.BasePermission):
    """
    Allow access only to authenticated Django staff users (is_staff=True).
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_staff)


class IsStaffOrReadOnly(permissions.BasePermission):
    """
    Read for everyone; write only for staff users.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_authenticated and request.user.is_staff)


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Read for everyone; write only for superusers.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_authenticated and request.user.is_superuser)
