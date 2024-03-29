from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("crm/clients/", include("apps.clients.urls")),
    path("crm/contracts/", include("apps.contracts.urls")),
    path("crm/events/", include("apps.events.urls")),
    path("", include("apps.users.urls")),
]

admin.site.site_header = "EpicEvents Admin"
admin.site.site_title = "EpicEvents Admin"
admin.site.index_title = "EpicEvents Admin"
