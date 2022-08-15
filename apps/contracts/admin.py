from django.contrib import admin

from .models import Contract


@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    fieldsets = (
        ("Contract Info", {"fields": ("client", "amount", "payment_due")}),
        ("Sales", {"fields": ("status", "sales_contact")}),
        ("Info", {"fields": ("date_created", "date_updated")}),
    )
    readonly_fields = ("date_created", "date_updated")
    list_display = (
        "contract_number",
        "sales_contact",
        "client",
        "amount",
        "payment_due",
        "status",
    )
    list_filter = ("status", "sales_contact")
    search_fields = ("contract_number", "client__last_name")

    @staticmethod
    def contract_number(obj):
        return f"Contract #{obj.id}"
