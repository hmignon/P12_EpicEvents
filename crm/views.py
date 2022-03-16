from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, generics
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Client, Contract, Event
from .permissions import (
    ClientPermissions,
    ContractPermissions,
    EventPermissions,
)
from .serializers import (
    ClientSerializer,
    ContractSerializer,
    EventSerializer,
)


class ClientList(generics.ListCreateAPIView):
    serializer_class = ClientSerializer
    permission_classes = [IsAuthenticated, ClientPermissions]
    filter_backends = [SearchFilter, DjangoFilterBackend]
    search_fields = ['^first_name', '^last_name', '^email', '^company_name']
    filterset_fields = ['status']

    def get_queryset(self):
        if self.request.user.team == 'SUPPORT':
            return Client.objects.filter(contract__event__support_contact=self.request.user).distinct()
        elif self.request.user.team == 'SALES':
            prospects = Client.objects.filter(status=False)
            own_clients = Client.objects.filter(sales_contact=self.request.user)
            return prospects | own_clients
        return Client.objects.all()

    def post(self, request, *args, **kwargs):
        serializer = ClientSerializer(data=request.data)

        if serializer.is_valid(raise_exception=True):
            if serializer.validated_data['status'] is True:
                serializer.validated_data['sales_contact'] = request.user
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ClientDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Client.objects.all()
    http_method_names = ['get', 'put', 'delete', 'options']
    permission_classes = [IsAuthenticated, ClientPermissions]
    serializer_class = ClientSerializer

    def update(self, request, *args, **kwargs):
        serializer = ClientSerializer(data=request.data)

        if serializer.is_valid(raise_exception=True):
            client = self.get_object()
            if client.status is True:
                if serializer.validated_data['status'] is False:
                    return Response('Cannot change status of converted client.', status=status.HTTP_403_FORBIDDEN)
            elif serializer.validated_data['status'] is True:
                serializer.validated_data['sales_contact'] = request.user

            serializer.save()
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ContractList(generics.ListCreateAPIView):
    serializer_class = ContractSerializer
    permission_classes = [IsAuthenticated, ContractPermissions]
    filter_backends = [SearchFilter, DjangoFilterBackend]
    search_fields = ['^client__first_name', '^client__last_name', '^client__email', '^client__company_name']
    filterset_fields = {
        'date_created': ['gte', 'lte'],
        'payment_due': ['gte', 'lte'],
        'amount': ['gte', 'lte'],
        'status': ['exact'],
    }

    def get_queryset(self):
        if self.request.user.team == 'SUPPORT':
            return Contract.objects.filter(event__support_contact=self.request.user)
        elif self.request.user.team == 'SALES':
            return Contract.objects.filter(sales_contact=self.request.user)
        return Contract.objects.all()

    def post(self, request, *args, **kwargs):
        serializer = ContractSerializer(data=request.data)

        if serializer.is_valid(raise_exception=True):
            serializer.validated_data['sales_contact'] = request.user
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ContractDetail(generics.RetrieveUpdateAPIView):
    queryset = Contract.objects.all()
    http_method_names = ['get', 'put', 'options']
    permission_classes = [IsAuthenticated, ContractPermissions]
    serializer_class = ContractSerializer


class EventList(generics.ListCreateAPIView):
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticated, EventPermissions]
    filter_backends = [SearchFilter, DjangoFilterBackend]
    search_fields = [
        '^contract__client__first_name', '^contract__client__last_name', '^contract__client__email',
        '^contract__client__company_name', '^name', '^location'
    ]
    filterset_fields = {
        'event_date': ['gte', 'lte'],
        'attendees': ['gte', 'lte'],
        'event_status': ['exact'],
    }

    def get_queryset(self):
        if self.request.user.team == 'SUPPORT':
            return Event.objects.filter(support_contact=self.request.user)
        elif self.request.user.team == 'SALES':
            return Event.objects.filter(contract__sales_contact=self.request.user)
        return Event.objects.all()

    def post(self, request, *args, **kwargs):
        serializer = EventSerializer(data=request.data)

        if serializer.is_valid(raise_exception=True):
            contract = generics.get_object_or_404(Contract, id=serializer.validated_data['contract'])
            if contract.status is False:
                return Response("The contract has not been signed.", status=status.HTTP_400_BAD_REQUEST)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EventDetail(generics.RetrieveUpdateAPIView):
    serializer_class = EventSerializer
    queryset = Event.objects.all()
    http_method_names = ['get', 'put', 'options']
    permission_classes = [IsAuthenticated, EventPermissions]

    def update(self, request, *args, **kwargs):
        event = self.get_object()
        serializer = EventSerializer(instance=event, data=request.data)

        if serializer.is_valid(raise_exception=True):
            if request.user.team == 'SUPPORT' and serializer.validated_data['contract'] != event.contract.id:
                return Response("You are not allowed to change the related contract.", status=status.HTTP_403_FORBIDDEN)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
