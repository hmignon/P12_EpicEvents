from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Client, Contract, Event
from .permissions import (
    ClientPermissions,
    ContractPermissions,
    EventPermissions
)
from .serializers import (
    ClientSerializer,
    ContractSerializer,
    EventSerializer,
)



