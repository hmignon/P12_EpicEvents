from rest_framework import serializers
from rest_framework.fields import CurrentUserDefault

from .models import Client, Contract, Event


class ClientSerializer(serializers.ModelSerializer):
    sales_contact = CurrentUserDefault()

    class Meta:
        model = Client
        fields = [
            'url', 'id', 'first_name', 'last_name', 'email', 'phone', 'mobile',
            'company_name', 'date_created', 'date_updated', 'sales_contact', 'status'
        ]
        read_only__fields = ('date_created', 'date_updated', 'sales_contact', 'id', 'url')


class ContractSerializer(serializers.ModelSerializer):
    sales_contact = CurrentUserDefault()
    client = serializers.PrimaryKeyRelatedField(queryset=Client.objects.filter(status='EXISTING'))

    class Meta:
        model = Contract
        fields = [
            'url', 'id', 'client', 'date_created', 'date_updated', 'sales_contact',
            'amount', 'payment_due', 'status'
        ]
        read_only__fields = ('date_created', 'date_updated', 'sales_contact', 'id', 'url')


class EventSerializer(serializers.ModelSerializer):
    client = serializers.PrimaryKeyRelatedField(queryset=Client.objects.filter(status='CONTRACT'))

    class Meta:
        model = Event
        fields = [
            'url', 'id', 'client', 'date_created', 'date_updated', 'support_contact',
            'attendees', 'event_status', 'event_date', 'notes'
        ]
        read_only__fields = ('date_created', 'date_updated', 'support_contact', 'id')
