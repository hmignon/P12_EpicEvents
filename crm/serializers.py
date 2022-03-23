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

    def validate_client(self, value):
        if value.status is False:
            raise serializers.ValidationError("The client is not converted.")
        return value


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = '__all__'
        read_only__fields = ['date_created', 'date_updated', 'support_contact', 'event_status', 'id']

    def validate_contract(self, value):
        if value.status is False:
            raise serializers.ValidationError("The contract is not signed.")
        return value
