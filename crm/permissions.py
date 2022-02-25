from rest_framework import permissions
from rest_framework.generics import get_object_or_404

from .models import Event, Client, Contract


class IsManager(permissions.BasePermission):
    """ Management team : all permissions granted """
    def has_permission(self, request, view):
        if request.user.team == 'MANAGEMENT':
            return True


class ProspectPermissions(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.team == 'SALES'


class ClientPermissions(permissions.BasePermission):
    """
    Sales team : can CREATE new clients or can VIEW and UPDATE their own clients
    Support team : can VIEW their own clients
    """
    def has_permission(self, request, view):
        try:
            client = get_object_or_404(Client, id=view.kwargs['pk'])
            if request.user.team == 'SUPPORT' and request.method in permissions.SAFE_METHODS:
                return client in Client.objects.filter(contract__event__support_contact=request.user.id)
            else:
                return request.user == client.sales_contact

        except KeyError:
            if request.user.team == 'SUPPORT':
                return request.method in permissions.SAFE_METHODS
            return request.user.team == 'SALES'


class ContractPermissions(permissions.BasePermission):
    """
        Sales team : can CREATE new contracts or can VIEW and UPDATE contracts of their own clients
        Support team : can VIEW contracts of their own clients
    """
    def has_permission(self, request, view):
        try:
            contract = get_object_or_404(Contract, id=view.kwargs['pk'])
            if request.user.team == 'SUPPORT' and request.method in permissions.SAFE_METHODS:
                return contract in Contract.objects.filter(event__support_contact=request.user.id)
            else:
                return request.user == contract.sales_contact

        except KeyError:
            if request.user.team == 'SUPPORT':
                return request.method in permissions.SAFE_METHODS
            return request.user.team == 'SALES'


class EventPermissions(permissions.BasePermission):
    """
        Sales team : can CREATE new events or can VIEW events of their own clients
        Support team : can VIEW and UPDATE events of their own clients
    """
    def has_permission(self, request, view):
        try:
            event = get_object_or_404(Event, id=view.kwargs['pk'])
            if request.user.team == 'SALES' and request.method in permissions.SAFE_METHODS:
                return event in Event.objects.filter(contract__sales_contact=request.user)
            else:
                return request.user == event.support_contact

        except KeyError:
            if request.user.team == 'SUPPORT':
                return request.method in permissions.SAFE_METHODS
            return request.user.team == 'SALES'
