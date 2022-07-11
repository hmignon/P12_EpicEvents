from rest_framework import permissions

from apps.users.models import MANAGEMENT


class IsManager(permissions.BasePermission):
    """ Managers have read_only permissions on the crm.
    Post, put or delete has to be done via the admin site.
    """

    def has_permission(self, request, view):
        return request.user.team.name == MANAGEMENT and request.method in permissions.SAFE_METHODS

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)
