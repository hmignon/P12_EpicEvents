from rest_framework import status
from rest_framework.reverse import reverse

from crm.models import Client, Contract, Event
from users.models import User
from .setup import CustomAPITestCase


class EventListTests(CustomAPITestCase):
    event_list_url = reverse('crm:event_list')

    # --- Managers ---
    def test_manager_get_event_list(self):
        """Managers can view all events in database"""
        user = User.objects.get(username='test_manager')
        test_client = self.get_token_auth_client(user)
        response = test_client.get(self.event_list_url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), len(Event.objects.all()))

    def test_manager_create_event(self):
        """Managers must create clients via admin site"""
        user = User.objects.get(username='test_manager')
        test_client = self.get_token_auth_client(user)
        data = {
            'client': 1,
            'amount': 1234.56,
            'payment_due': '2022-10-09',
            'status': False
        }
        response = test_client.post(self.event_list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # --- Sales ---
    def test_sales_get_event_list(self):
        """Sales can view their own events"""
        user = User.objects.get(username='test_sales')
        test_client = self.get_token_auth_client(user)
        response = test_client.get(self.event_list_url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for item in response.data:
            self.assertEqual(Event.objects.get(contract=item['contract']).contract.sales_contact, user)

    def test_sales_create_event(self):
        """Sales can create an event for a contract"""
        user = User.objects.get(username='test_sales')
        test_client = self.get_token_auth_client(user)
        contract = Contract.objects.create(
            client=Client.objects.get(id=1), amount=123.45, payment_due='2022-06-09', status=True
        )
        data = {
            'contract': contract.id,
            'name': 'Example event',
            'attendees': 50,
            'event_date': '2022-10-09'
        }
        response = test_client.post(self.event_list_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertFalse(Event.objects.get(contract=response.data['contract']).event_status)

    def test_sales_create_event_unsigned_contract(self):
        """Sales not allowed to create contract for unconverted client"""
        user = User.objects.get(username='test_sales')
        test_client = self.get_token_auth_client(user)
        data = {
            'contract': 2,
            'name': 'Example event',
            'attendees': 50,
            'event_date': '2022-10-09'
        }
        response = test_client.post(self.event_list_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_sales_post_event_incomplete_data(self):
        """Check validation for missing fields in request"""
        user = User.objects.get(username='test_sales')
        test_client = self.get_token_auth_client(user)
        response = test_client.post(self.event_list_url, data={'name': 'test'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # --- Support ---
    def test_support_get_event_list(self):
        """Support can view their own events (support_contact)"""
        user = User.objects.get(username='test_support')
        test_client = self.get_token_auth_client(user)
        response = test_client.get(self.event_list_url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for item in response.data:
            self.assertEqual(user.id, item['support_contact'])

    def test_support_create_event(self):
        """Support not allowed to create an event"""
        user = User.objects.get(username='test_support')
        test_client = self.get_token_auth_client(user)
        contract = Contract.objects.create(
            client=Client.objects.get(id=1), amount=123.45, payment_due='2022-06-09', status=True
        )
        data = {
            'contract': contract.id,
            'name': 'Example event',
            'attendees': 50,
            'event_date': '2022-10-09'
        }
        response = test_client.post(self.event_list_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class EventDetailTests(CustomAPITestCase):

    # --- Managers ---
    def test_manager_get_event_detail(self):
        """Managers can view any event in database"""
        user = User.objects.get(username='test_manager')
        test_client = self.get_token_auth_client(user)
        id_list = self.get_id_list(Event.objects.all())

        for i in range(len(id_list)):
            response = test_client.get(reverse('crm:event_detail', kwargs={'pk': id_list[i]}))
            self.assertEqual(response.status_code, status.HTTP_200_OK)

    # --- Sales ---
    def test_sales_get_event_detail(self):
        """Sales can view their own events"""
        user = User.objects.get(username='test_sales')
        test_client = self.get_token_auth_client(user)
        id_list = self.get_id_list(Event.objects.all())

        for i in range(len(id_list)):
            response = test_client.get(reverse('crm:event_detail', kwargs={'pk': id_list[i]}))
            if Event.objects.get(id=id_list[i]).contract.sales_contact != user:
                self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
            else:
                self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_sales_update_event(self):
        """Sales can update event if not finished"""
        user = User.objects.get(username='test_sales')
        test_client = self.get_token_auth_client(user)
        data = {
            'contract': 1,
            'name': 'Upcoming with support updated',
            'location': 'Le Shed',
            'attendees': 160,
            'event_date': '2022-09-10',
            'notes': 'Example note'
        }
        response = test_client.put('/crm/events/1/', data)

        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertEqual('Upcoming with support updated', response.data['name'])

    def test_sales_update_finished_event(self):
        """Sales not allowed to update event if finished"""
        user = User.objects.get(username='test_sales')
        test_client = self.get_token_auth_client(user)
        data = {
            'contract': 4,
            'name': 'Finished event updated',
            'attendees': 78,
            'event_date': '2022-09-10'
        }
        response = test_client.put('/crm/events/3/', data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.json(), {"detail": "Cannot update a finished event."})

    def test_sales_update_event_contract(self):
        """Sales not allowed to update contract related to an event"""
        user = User.objects.get(username='test_sales')
        test_client = self.get_token_auth_client(user)
        contract = Contract.objects.create(
            client=Client.objects.get(id=1), amount=123.45, payment_due='2022-06-09', status=True
        )
        data = {
            'contract': contract.id,
            'name': 'Upcoming with support Updated',
            'location': 'Le Shed',
            'attendees': 160,
            'event_date': '2022-09-10',
            'notes': 'Example note'
        }
        response = test_client.put('/crm/events/1/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), {"detail": "Cannot change the related contract."})

    def test_update_event_incomplete_data(self):
        """Check validation for missing fields in request"""
        user = User.objects.get(username='test_sales')
        test_client = self.get_token_auth_client(user)
        response = test_client.put('/crm/events/1/', data={'name': 'test'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # --- Support ---
    def test_support_get_event_detail(self):
        """Support can only view their own event (support_contact)"""
        user = User.objects.get(username='test_support')
        test_client = self.get_token_auth_client(user)

        response = test_client.get(reverse('crm:event_detail', kwargs={'pk': 1}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = test_client.get(reverse('crm:event_detail', kwargs={'pk': 2}))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_support_update_event(self):
        """Support can update event if not finished"""
        user = User.objects.get(username='test_support')
        test_client = self.get_token_auth_client(user)
        data = {
            'contract': 1,
            'name': 'Upcoming with support updated',
            'location': 'Location updated',
            'attendees': 160,
            'event_date': '2022-09-10',
            'notes': 'Example note updated'
        }
        response = test_client.put('/crm/events/1/', data)

        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertEqual('Location updated', response.data['location'])

    def test_support_update_finished_event(self):
        """Support not allowed to update event if finished"""
        user = User.objects.get(username='test_support')
        test_client = self.get_token_auth_client(user)
        data = {
            'contract': 4,
            'name': 'Finished event updated',
            'attendees': 78,
            'event_date': '2022-09-10'
        }
        response = test_client.put('/crm/events/3/', data)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.json(), {"detail": "Cannot update a finished event."})

    def test_support_update_event_contract(self):
        """Support not allowed to update contract related to an event"""
        user = User.objects.get(username='test_support')
        test_client = self.get_token_auth_client(user)
        contract = Contract.objects.create(
            client=Client.objects.get(id=1), amount=123.45, payment_due='2022-06-09', status=True
        )
        data = {
            'contract': contract.id,
            'name': 'Upcoming with support Updated',
            'location': 'Le Shed',
            'attendees': 160,
            'event_date': '2022-09-10',
            'notes': 'Example note'
        }
        response = test_client.put('/crm/events/1/', data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), {"detail": "Cannot change the related contract."})
