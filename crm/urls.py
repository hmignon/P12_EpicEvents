from django.urls import path

from . import views


urlpatterns = [
    path('', views.api_root),
    path('clients/', views.ClientList.as_view(), name='client-list'),
    path('clients/<int:pk>/detail/', views.ClientDetail.as_view(), name='client-detail'),
    path('contracts/', views.ContractList.as_view(), name='contract-list'),
    path('contracts/<int:pk>/detail/', views.ContractDetail.as_view(), name='contract-detail'),
    path('events/', views.EventList.as_view(), name='event-list'),
    path('events/<int:pk>/detail/', views.EventDetail.as_view(), name='event-detail'),
]
