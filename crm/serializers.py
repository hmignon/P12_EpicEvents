from rest_framework import serializers

from .models import Client, Contract, Event


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = '__all__'
        read_only__fields = ['date_created', 'date_updated', 'sales_contact', 'id']


class ContractSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contract
        fields = '__all__'
        read_only__fields = ['date_created', 'date_updated', 'sales_contact', 'id']


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = '__all__'
        read_only__fields = ['date_created', 'date_updated', 'support_contact', 'id']
