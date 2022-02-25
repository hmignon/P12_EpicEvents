from rest_framework import serializers
from rest_framework.fields import CurrentUserDefault

from .models import Client, Contract, Event


class ClientSerializer(serializers.ModelSerializer):
    sales_contact = CurrentUserDefault()

    class Meta:
        model = Client
        fields = '__all__'
        read_only__fields = ('date_created', 'date_updated', 'sales_contact', 'id')


class ContractSerializer(serializers.ModelSerializer):
    sales_contact = CurrentUserDefault()
    client = serializers.PrimaryKeyRelatedField(queryset=Client.objects.filter(status='EXISTING'))

    class Meta:
        model = Contract
        fields = '__all__'
        read_only__fields = ('date_created', 'date_updated', 'sales_contact', 'id')


class EventSerializer(serializers.ModelSerializer):
    client = serializers.PrimaryKeyRelatedField(queryset=Client.objects.filter(status='CONTRACT'))

    class Meta:
        model = Event
        fields = '__all__'
        read_only__fields = ('date_created', 'date_updated', 'support_contact', 'id')
