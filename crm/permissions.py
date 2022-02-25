from rest_framework import permissions
from rest_framework.generics import get_object_or_404

from .models import Event, Client, Contract


class ClientPermissions(permissions.BasePermission):
    def has_permission(self, request, view):
        try:
            client = get_object_or_404(Client, id=view.kwargs['pk'])
            if request.method in ['PUT', 'PATCH']:
                return request.user == client.sales_contact or request.user.team == 'MANAGEMENT'
            return request.method in permissions.SAFE_METHODS
        except KeyError:
            if request.user.team == 'SUPPORT':
                return request.method in permissions.SAFE_METHODS
            return request.user.team in ['MANAGEMENT', 'SALES']


class ContractPermissions(permissions.BasePermission):
    def has_permission(self, request, view):
        try:
            contract = get_object_or_404(Contract, id=view.kwargs['pk'])
            if request.method in ['PUT', 'PATCH']:
                return request.user == contract.sales_contact or request.user.team == 'MANAGEMENT'
            return request.method in permissions.SAFE_METHODS
        except KeyError:
            if request.user.team == 'SUPPORT':
                return request.method in permissions.SAFE_METHODS
            return request.user.team in ['MANAGEMENT', 'SALES']


class EventPermissions(permissions.BasePermission):
    def has_permission(self, request, view):
        try:
            event = get_object_or_404(Event, id=view.kwargs['pk'])
            if request.method in ['PUT', 'PATCH']:
                return request.user == event.support_contact or request.user.team == 'MANAGEMENT'
            return request.method in permissions.SAFE_METHODS
        except KeyError:
            if request.user.team == 'SUPPORT':
                return request.method in permissions.SAFE_METHODS
            return request.user.team in ['MANAGEMENT', 'SALES']
