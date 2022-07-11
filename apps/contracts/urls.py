from django.urls import path

from . import views

app_name = 'contracts'
urlpatterns = [
    path('', views.ContractList.as_view(), name='list'),
    path('<int:pk>/', views.ContractDetail.as_view(), name='detail'),
]
