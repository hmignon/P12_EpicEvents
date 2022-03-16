from django.core.management import call_command
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from crm.models import Client, Contract, Event
from users.models import User


class ClientListTests(APITestCase):
    password = 'test_password'
    login_url = reverse('login')
    client_list_url = reverse('client-list')

    def setUp(self):
        User.objects.create_user(
            id=1, username='test_manager', password='test_password', email='test_manager@email.com', team='MANAGEMENT'
        )
        User.objects.create_user(
            id=2, username='test_sales', password='test_password', email='test_sales@email.com', team='SALES'
        )
        User.objects.create_user(
            id=3, username='test_support', password='test_password', email='test_support@email.com', team='SUPPORT'
        )
        call_command('loaddata', 'crm/fixtures/data.json', verbosity=0)

    def get_token(self, user):
        data = {
            'username': user.username,
            'password': self.password,
        }
        response = self.client.post(self.login_url, data, format='json')
        token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        return self.client

    def test_manager_get_client_list(self):
        """Managers get all clients in database"""
        user = User.objects.get(username='test_manager')
        test_client = self.get_token(user)
        response = test_client.get(self.client_list_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), len(Client.objects.all()))

    def test_sales_get_client_list(self):
        """Sales get their own clients and unconverted clients"""
        user = User.objects.get(username='test_sales')
        test_client = self.get_token(user)
        response = test_client.get(self.client_list_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for item in response.data:
            if item['status'] is True:
                self.assertEqual(item['sales_contact'], user.id)
            else:
                self.assertFalse(item['status'])

    def test_support_get_client_list(self):
        """Support get their own clients (support_contact)"""
        user = User.objects.get(username='test_support')
        test_client = self.get_token(user)

        response = test_client.get(self.client_list_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for item in response.data:
            client = Client.objects.get(id=item['id'])
            self.assertIn(client, Client.objects.filter(contract__event__support_contact=user.id))

    def test_sales_post_prospect(self):
        """Sales can post new prospect"""
        user = User.objects.get(username='test_sales')
        test_client = self.get_token(user)
        data = {
            'first_name': 'first_name',
            'last_name': 'last_name',
            'email': 'test_client@email.com',
            'status': False
        }
        response = test_client.post(self.client_list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual('test_client@email.com', response.data['email'])

    def test_sales_post_client(self):
        """Sales can post new client
        Check if sales_contact is user
        """
        user = User.objects.get(username='test_sales')
        test_client = self.get_token(user)
        data = {
            'first_name': 'first_name',
            'last_name': 'last_name',
            'email': 'test_client@email.com',
            'status': True
        }
        response = test_client.post(self.client_list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('test_client@email.com', response.data['email'])
        self.assertEqual(user.id, response.data['sales_contact'])

    def test_support_post_client(self):
        """Support not allowed to post new clients/prospects"""
        user = User.objects.get(username='test_support')
        test_client = self.get_token(user)
        data = {
            'first_name': 'first_name',
            'last_name': 'last_name',
            'email': 'test_client@email.com',
            'status': False
        }
        response = test_client.post(self.client_list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_sales_get_client_detail(self):
        """Sales get client if their own client or unconverted client"""
        user = User.objects.get(username='test_sales')
        test_client = self.get_token(user)
        for i in range(len(Client.objects.all())):
            response = test_client.get(reverse('client-detail', kwargs={'pk': i+1}))
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            if response.data['status'] is True:
                self.assertEqual(Client.objects.get(id=i+1).sales_contact, user)
            else:
                self.assertFalse(Client.objects.get(id=i+1).status)

    def test_support_get_client_detail(self):
        """Support get client only if their own client (support_contact)"""
        user = User.objects.get(username='test_support')
        test_client = self.get_token(user)
        response = test_client.get(reverse('client-detail', kwargs={'pk': 1}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = test_client.get(reverse('client-detail', kwargs={'pk': 3}))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_sales_update_client(self):
        """Sales can update client if their own client or unconverted client
        If status is True, check if sales_contact is user
        """
        user = User.objects.get(username='test_sales')
        test_client = self.get_token(user)
        data = {
            'first_name': 'John',
            'last_name': 'Smith',
            'email': 'updated_email@email.com',
            'status': True
        }
        response = test_client.put('/crm/clients/3/', data)
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertEqual('updated_email@email.com', response.data['email'])
        self.assertEqual(response.data['sales_contact'], user.id)

    def test_update_converted_client_status(self):
        """Sales not allowed to update client status is True"""
        user = User.objects.get(username='test_sales')
        test_client = self.get_token(user)
        data = {
            'first_name': 'James',
            'last_name': 'Miller',
            'email': 'email@email.com',
            'status': False
        }
        response = test_client.put('/crm/clients/1/', data)
        self.assertEqual(
            response.status_code, status.HTTP_403_FORBIDDEN, msg='Cannot change status of converted client.'
        )

    def test_support_update_client(self):
        """Support not allowed to update client"""
        user = User.objects.get(username='test_support')
        test_client = self.get_token(user)
        data = {
            'first_name': 'John',
            'last_name': 'Smith',
            'email': 'updated_email@email.com',
            'status': True
        }
        response = test_client.put('/crm/clients/4/', data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_sales_delete_prospect(self):
        """Sales can delete client if status is False"""
        user = User.objects.get(username='test_sales')
        test_client = self.get_token(user)
        response = test_client.delete(reverse('client-detail', kwargs={'pk': 4}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_converted_client(self):
        """Sales not allowed to delete client if status is True"""
        user = User.objects.get(username='test_sales')
        test_client = self.get_token(user)
        response = test_client.delete(reverse('client-detail', kwargs={'pk': 1}))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
