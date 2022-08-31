from django.contrib import admin

from .models import Client


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    fieldsets = (
        (
            "Client/Prospect Info",
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "company_name",
                    "email",
                    "phone",
                    "mobile",
                )
            },
        ),
        ("Sales", {"fields": ("status", "sales_contact")}),
        ("Info", {"fields": ("date_created", "date_updated")}),
    )
    readonly_fields = ("date_created", "date_updated")
    list_display = (
        "full_name",
        "company_name",
        "email",
        "phone",
        "mobile",
        "status",
        "sales_contact",
    )
    list_filter = ("status", "sales_contact")
    search_fields = ("first_name", "last_name", "company_name", "sales_contact")

    @staticmethod
    def full_name(obj):
        return f"{obj.last_name}, {obj.first_name}"
