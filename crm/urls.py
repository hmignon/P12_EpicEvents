from django.urls import path

from . import views

app_name = 'crm'
urlpatterns = [
    path('clients/', views.ClientList.as_view(), name='client_list'),
    path('clients/<int:pk>/', views.ClientDetail.as_view(), name='client_detail'),
    path('contracts/', views.ContractList.as_view(), name='contract_list'),
    path('contracts/<int:pk>/', views.ContractDetail.as_view(), name='contract_detail'),
    path('events/', views.EventList.as_view(), name='event_list'),
    path('events/<int:pk>/', views.EventDetail.as_view(), name='event_detail'),
]
