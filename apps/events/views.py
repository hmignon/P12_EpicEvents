from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, status
from rest_framework.exceptions import ValidationError
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.common.permissions import IsManager
from apps.users.models import SALES, SUPPORT
from .models import Event
from .permissions import EventPermissions
from .serializers import EventSerializer


class EventList(generics.ListCreateAPIView):
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticated, IsManager | EventPermissions]
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
        if self.request.user.team.name == SUPPORT:
            return Event.objects.filter(support_contact=self.request.user)
        elif self.request.user.team.name == SALES:
            return Event.objects.filter(contract__sales_contact=self.request.user)
        return Event.objects.all()

    def post(self, request, *args, **kwargs):
        serializer = EventSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)


class EventDetail(generics.RetrieveUpdateAPIView):
    queryset = Event.objects.all()
    http_method_names = ['get', 'put', 'options']
    permission_classes = [IsAuthenticated, IsManager | EventPermissions]
    serializer_class = EventSerializer

    def update(self, request, *args, **kwargs):
        event = self.get_object()
        serializer = EventSerializer(instance=event, data=request.data)
        if serializer.is_valid(raise_exception=True):
            if serializer.validated_data['contract'] != event.contract:
                raise ValidationError({"detail": "Cannot change the related contract."})
            serializer.validated_data['support_contact'] = event.support_contact
            serializer.save()
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
