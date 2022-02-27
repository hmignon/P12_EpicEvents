from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView

from .views import UpdatePassword

urlpatterns = [
    path('login/', TokenObtainPairView.as_view(), name='login'),
    path('update-password/', UpdatePassword.as_view(), name='update-password'),
]
