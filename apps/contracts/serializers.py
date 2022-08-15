from rest_framework import serializers

from .models import Contract


class ContractSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contract
        fields = "__all__"
        read_only__fields = ["date_created", "date_updated", "sales_contact", "id"]
