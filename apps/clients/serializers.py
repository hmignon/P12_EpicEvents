from rest_framework import serializers

from .models import Client


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = '__all__'
        read_only__fields = ['date_created', 'date_updated', 'sales_contact', 'id']
