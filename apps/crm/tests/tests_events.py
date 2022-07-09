from rest_framework import status
from rest_framework.reverse import reverse

from apps.common.tests.setup import CustomCRMTestCase
from apps.crm.models import Event
from apps.users.models import User


class EventListTests(CustomCRMTestCase):
    event_list_url = reverse('crm:event_list')
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
            response = test_client.get(reverse('crm:event_detail', kwargs={'pk': event_id}))
            self.assertEqual(response.status_code, status.HTTP_200_OK)

    # --- Sales ---
    def test_sales_get_event_detail(self):
        """Sales can view their own events."""
        user = User.objects.get(username='test_sales')
        test_client = self.get_token_auth_client(user)
        for event_id in self.get_id_list(Event.objects.all()):
            response = test_client.get(reverse('crm:event_detail', kwargs={'pk': event_id}))
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
        response1 = test_client.get(reverse('crm:event_detail', kwargs={'pk': 1}))
        response2 = test_client.get(reverse('crm:event_detail', kwargs={'pk': 2}))
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
