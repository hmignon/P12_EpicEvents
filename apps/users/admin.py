from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group

from .models import User

admin.site.unregister(Group)


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = (
        (
            "Personal Info",
            {
                "fields": (
                    "username",
                    "password",
                    "first_name",
                    "last_name",
                    "email",
                    "phone",
                    "mobile",
                )
            },
        ),
        ("Permissions", {"fields": ("team",)}),
        ("Important Dates", {"fields": ("date_joined", "last_login")}),
    )
    readonly_fields = ("date_joined", "last_login")
    list_display = (
        "username",
        "first_name",
        "last_name",
        "email",
        "phone",
        "mobile",
        "team",
    )
    list_filter = ("team", "is_active")
