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
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    permission_classes = [IsAuthenticated, ClientPermissions]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filter_fields = ['status', 'sales_contact']
    search_fields = ['first_name', 'last_name', 'email', 'company_name']

    def post(self, request, *args, **kwargs):
        data = request.data.copy()
        data['sales_contact'] = request.user.id
        serializer = ClientSerializer(data=data, context={"request": self.request})

        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ClientDetail(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated, ClientPermissions]
    serializer_class = ClientSerializer
    lookup_field = 'pk'

    def get_object(self):
        return generics.get_object_or_404(Client, pk=self.kwargs["pk"])


class ContractList(generics.ListCreateAPIView):
    queryset = Contract.objects.all()
    serializer_class = ContractSerializer
    permission_classes = [IsAuthenticated, ContractPermissions]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filter_fields = ['status', 'sales_contact', 'date_created', 'payment_due', 'amount']
    search_fields = [
        'client__first_name', 'client__last_name', 'client__email', 'client__company_name',
    ]

    def post(self, request, *args, **kwargs):
        data = request.data.copy()
        data['sales_contact'] = request.user.id
        serializer = ContractSerializer(data=data, context={"request": self.request})

        if Client.objects.get(id=data['client']).status == "POTENTIAL":
            return Response("Client not converted.", status=status.HTTP_400_BAD_REQUEST)
        elif Client.objects.get(id=data['client']).status == "CONTRACT":
            return Response("Client already under contract.", status=status.HTTP_400_BAD_REQUEST)

        if serializer.is_valid(raise_exception=True):
            contract = serializer.save()
            client = Client.objects.get(id=contract.client.id)
            client.status = 'CONTRACT'
            client.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ContractDetail(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated, ContractPermissions]
    serializer_class = ContractSerializer
    lookup_field = 'pk'

    def get_object(self):
        return generics.get_object_or_404(Contract, pk=self.kwargs["pk"])


class EventList(generics.ListCreateAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticated, EventPermissions]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filter_fields = ['support_contact', 'event_date', 'event_status', 'attendees']
    search_fields = [
        'client__first_name', 'client__last_name', 'client__email', 'client__company_name',
    ]

    def post(self, request, *args, **kwargs):
        data = request.data.copy()

        if Client.objects.get(id=data['client']).status != "CONTRACT":
            return Response("No contract signed.", status=status.HTTP_400_BAD_REQUEST)

        serializer = EventSerializer(data=data, context={"request": self.request})

        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EventDetail(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated, EventPermissions]
    serializer_class = EventSerializer
    lookup_field = 'pk'

    def get_object(self):
        return generics.get_object_or_404(Event, pk=self.kwargs["pk"])
