import datetime

from django.core.management import call_command
from rest_framework import status
from rest_framework.reverse import reverse

from apps.common.tests.setup import CommandTestCase, CustomCRMTestCase
from apps.contracts.models import Contract
from apps.users.models import User
from .models import Event

EVENT_COMMAND = "create_events"


class EventCommandTests(CommandTestCase):

    @staticmethod
    def create_sample_data():
        call_command("create_users", "--verbosity=0")
        call_command("create_clients", "--verbosity=0")
        call_command("create_contracts", "--verbosity=0")

    def test_create_events_default(self):
        self.create_sample_data()
        contracts = Contract.objects.filter(status=True).count()
        events_before = Event.objects.all().count()
        out = self.call_command(EVENT_COMMAND)
        if contracts < 10:
            self.assertEqual(out, f"Maximum events possible: {contracts}\nCreating {contracts} event(s)...\n")
            self.assertEqual(Event.objects.all().count(), events_before + contracts)
        else:
            self.assertEqual(out, "Creating 10 event(s)...\n")
            self.assertEqual(Event.objects.all().count(), events_before + 10)
            contracts = 20

        # test created data
        events = Event.objects.all().order_by('-id')[:contracts]
        for event in events:
            self.assertEqual(type(event.contract_id), int)
            self.assertEqual(type(event.name), str)
            self.assertEqual(type(event.location), str)
            if event.support_contact:
                self.assertEqual(type(event.support_contact_id), int)
                self.assertEqual(event.support_contact.team_id, 3)
            self.assertEqual(type(event.event_status), bool)
            self.assertEqual(type(event.attendees), int)
            self.assertEqual(type(event.event_date), datetime.datetime)
            self.assertEqual(type(event.notes), str)

    def test_create_events_with_args(self):
        self.create_sample_data()
        events_before = Event.objects.all().count()
        out = self.call_command(EVENT_COMMAND, "-n 2")
        self.assertEqual(out, "Creating 2 event(s)...\n")
        self.assertEqual(Event.objects.all().count(), events_before + 2)

        events_before = Event.objects.all().count()
        out = self.call_command(EVENT_COMMAND, "--number=1")
        self.assertEqual(out, "Creating 1 event(s)...\n")
        self.assertEqual(Event.objects.all().count(), events_before + 1)


class EventListTests(CustomCRMTestCase):
    event_list_url = reverse('events:list')
    event_create_data = {
        'name': 'Example event',
        'attendees': 50,
        'event_date': '2022-10-09'
    }

    # --- Managers ---
    def test_manager_get_event_list(self):
        """Managers can view all events in database."""
        user = User.objects.get(username='test_manager')
        test_client = self.get_token_auth_client(user)
        response = test_client.get(self.event_list_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), len(Event.objects.all()))

    def test_manager_create_event(self):
        """Managers must create events via admin site."""
        user = User.objects.get(username='test_manager')
        test_client = self.get_token_auth_client(user)
        response = test_client.post(self.event_list_url, self.event_create_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # --- Sales ---
    def test_sales_get_event_list(self):
        """Sales can view their own events."""
        user = User.objects.get(username='test_sales')
        test_client = self.get_token_auth_client(user)
        response = test_client.get(self.event_list_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for item in response.data:
            self.assertEqual(Event.objects.get(contract=item['contract']).contract.sales_contact, user)

    def test_sales_create_event(self):
        """Sales can create an event for a contract."""
        user = User.objects.get(username='test_sales')
        test_client = self.get_token_auth_client(user)
        self.event_create_data['contract'] = self.create_contract().id
        response = test_client.post(self.event_list_url, self.event_create_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertFalse(Event.objects.get(contract=response.data['contract']).event_status)

    def test_sales_create_event_unsigned_contract(self):
        """Sales not allowed to create contract for unconverted client."""
        user = User.objects.get(username='test_sales')
        test_client = self.get_token_auth_client(user)
        data = self.event_create_data
        data["contract"] = 2
        response = test_client.post(self.event_list_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_sales_post_event_incomplete_data(self):
        """Check validation for missing fields in request."""
        user = User.objects.get(username='test_sales')
        test_client = self.get_token_auth_client(user)
        response = test_client.post(self.event_list_url, data={'name': 'test'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # --- Support ---
    def test_support_get_event_list(self):
        """Support can view their own events (support_contact)."""
        user = User.objects.get(username='test_support')
        test_client = self.get_token_auth_client(user)
        response = test_client.get(self.event_list_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for item in response.data:
            self.assertEqual(user.id, item['support_contact'])

    def test_support_create_event(self):
        """Support not allowed to create an event."""
        user = User.objects.get(username='test_support')
        test_client = self.get_token_auth_client(user)
        self.event_create_data['contract'] = self.create_contract().id
        response = test_client.post(self.event_list_url, self.event_create_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class EventDetailTests(CustomCRMTestCase):
    event_detail_url = 'events:detail'
    event_update_data = {
        'name': 'UPDATED',
        'location': 'Le Shed',
        'attendees': 160,
        'event_date': '2022-09-10',
        'notes': 'Example note'
    }
    finished_event_data = {
        'contract': 4,
        'name': 'Finished event updated',
        'attendees': 78,
        'event_date': '2022-09-10'
    }

    # --- Managers ---
    def test_manager_get_event_detail(self):
        """Managers can view any event in database."""
        user = User.objects.get(username='test_manager')
        test_client = self.get_token_auth_client(user)
        for event_id in self.get_id_list(Event.objects.all()):
            response = test_client.get(reverse(self.event_detail_url, kwargs={'pk': event_id}))
            self.assertEqual(response.status_code, status.HTTP_200_OK)

    # --- Sales ---
    def test_sales_get_event_detail(self):
        """Sales can view their own events."""
        user = User.objects.get(username='test_sales')
        test_client = self.get_token_auth_client(user)
        for event_id in self.get_id_list(Event.objects.all()):
            response = test_client.get(reverse(self.event_detail_url, kwargs={'pk': event_id}))
            if Event.objects.get(id=event_id).contract.sales_contact != user:
                self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
            else:
                self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_sales_update_event(self):
        """Sales can update event if not finished."""
        user = User.objects.get(username='test_sales')
        test_client = self.get_token_auth_client(user)
        self.event_update_data['contract'] = 1
        response = test_client.put('/crm/events/1/', self.event_update_data)
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertEqual('UPDATED', response.data['name'])

    def test_sales_update_finished_event(self):
        """Sales not allowed to update event if finished."""
        user = User.objects.get(username='test_sales')
        test_client = self.get_token_auth_client(user)
        response = test_client.put('/crm/events/3/', self.finished_event_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.json(), {"detail": "Cannot update a finished event."})

    def test_sales_update_event_contract(self):
        """Sales not allowed to update contract related to an event."""
        user = User.objects.get(username='test_sales')
        test_client = self.get_token_auth_client(user)
        self.event_update_data['contract'] = self.create_contract().id
        response = test_client.put('/crm/events/1/', self.event_update_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), {"detail": "Cannot change the related contract."})

    def test_update_event_incomplete_data(self):
        """Check validation for missing fields in request."""
        user = User.objects.get(username='test_sales')
        test_client = self.get_token_auth_client(user)
        response = test_client.put('/crm/events/1/', data={'name': 'test'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # --- Support ---
    def test_support_get_event_detail(self):
        """Support can only view their own event (support_contact)."""
        user = User.objects.get(username='test_support')
        test_client = self.get_token_auth_client(user)
        response1 = test_client.get(reverse(self.event_detail_url, kwargs={'pk': 1}))
        response2 = test_client.get(reverse(self.event_detail_url, kwargs={'pk': 2}))
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        self.assertEqual(response2.status_code, status.HTTP_403_FORBIDDEN)

    def test_support_update_event(self):
        """Support can update event if not finished."""
        user = User.objects.get(username='test_support')
        test_client = self.get_token_auth_client(user)
        self.event_update_data['contract'] = 1
        response = test_client.put('/crm/events/1/', self.event_update_data)
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertEqual('UPDATED', response.data['name'])

    def test_support_update_finished_event(self):
        """Support not allowed to update event if finished."""
        user = User.objects.get(username='test_support')
        test_client = self.get_token_auth_client(user)
        response = test_client.put('/crm/events/3/', self.finished_event_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.json(), {"detail": "Cannot update a finished event."})

    def test_support_update_event_contract(self):
        """Support not allowed to update contract related to an event."""
        user = User.objects.get(username='test_support')
        test_client = self.get_token_auth_client(user)
        data = self.event_update_data
        data['contract'] = self.create_contract().id
        response = test_client.put('/crm/events/1/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), {"detail": "Cannot change the related contract."})


class EventModelTests(CustomCRMTestCase):

    def test_str_event(self):
        event = Event.objects.get(id=1)
        self.assertEqual(str(event), "Event #1 : Miller, James | Date : 2022-03-06 (UPCOMING)")
        event = Event.objects.get(id=3)
        self.assertEqual(str(event), "Event #3 : Dupont, Jean | Date : 2022-11-17 (COMPLETED)")
