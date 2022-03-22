from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import get_object_or_404

from .models import Event, Client, Contract
from users.models import MANAGEMENT, SALES, SUPPORT


class ClientPermissions(permissions.BasePermission):
    """
        Management : all permissions granted
        Sales team : can CREATE new clients / prospects
                     can VIEW and UPDATE any prospect and their own clients
                     can DELETE prospects only
        Support team : can VIEW their own clients
    """

    def has_permission(self, request, view):
        if request.user.team == MANAGEMENT:
            return True
        elif request.user.team == SUPPORT:
            return request.method in permissions.SAFE_METHODS
        return request.user.team == SALES

    def has_object_permission(self, request, view, obj):
        if request.method == 'DELETE':
            return request.user.team == SALES and obj.status is False
        elif request.user.team == SUPPORT and request.method in permissions.SAFE_METHODS:
            return obj in Client.objects.filter(contract__event__support_contact=request.user)
        elif request.user.team == SALES:
            return request.user == obj.sales_contact or obj.status is False


class ContractPermissions(permissions.BasePermission):
    """
        Management : all permissions granted
        Sales team : can CREATE new contracts
                     can VIEW and UPDATE contracts of their own clients if not signed
        Support team : can VIEW contracts of their own clients
    """

    def has_permission(self, request, view):
        if request.user.team == MANAGEMENT:
            return True
        elif request.user.team == SUPPORT:
            return request.method in permissions.SAFE_METHODS
        return request.user.team == SALES

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            if request.user.team == SUPPORT:
                return obj in Contract.objects.filter(event__support_contact=request.user)
            elif request.user.team == SALES:
                return request.user == obj.sales_contact
        elif request.method == 'PUT' and obj.status is True:
            raise PermissionDenied("Cannot update a signed contract.")
        return request.user == obj.sales_contact and obj.status is False


class EventPermissions(permissions.BasePermission):
    """
        Management : all permissions granted
        Sales team : can CREATE new events
                     can VIEW events of their own clients
                     can UPDATE events of their own clients if not finished
        Support team : can VIEW events of their own clients
                       can UPDATE events of their own clients if not finished
    """

    def has_permission(self, request, view):
        if request.user.team == MANAGEMENT:
            return True
        elif request.user.team == SUPPORT:
            return request.method in ['GET', 'PUT']
        return request.user.team == SALES

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return request.user == obj.support_contact or request.user == obj.contract.sales_contact
        else:
            if obj.event_status is True:
                raise PermissionDenied("Cannot update a finished event.")
            if request.user.team == SUPPORT:
                return request.user == obj.support_contact
            elif request.user.team == SALES:
                return request.user == obj.contract.sales_contact
