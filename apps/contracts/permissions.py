from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied

from apps.users.models import SALES, SUPPORT
from .models import Contract


class ContractPermissions(permissions.BasePermission):
    """Sales team : can CREATE new contracts
                 can VIEW and UPDATE contracts of their own clients if not signed
    Support team : can VIEW contracts of their own clients
    """

    def has_permission(self, request, view):
        if request.user.team.name == SUPPORT:
            return request.method in permissions.SAFE_METHODS
        return request.user.team.name == SALES

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            if request.user.team.name == SUPPORT:
                return obj in Contract.objects.filter(
                    event__support_contact=request.user
                )
            return request.user == obj.sales_contact
        elif request.method == "PUT" and obj.status is True:
            raise PermissionDenied("Cannot update a signed contract.")
        return request.user == obj.sales_contact and obj.status is False
