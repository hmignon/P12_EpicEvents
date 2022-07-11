from rest_framework import serializers

from .models import Event


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = '__all__'
        read_only__fields = ['date_created', 'date_updated', 'support_contact', 'event_status', 'id']
