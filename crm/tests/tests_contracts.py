from rest_framework import status
from rest_framework.reverse import reverse

from crm.models import Client, Contract
from users.models import User
from .setup import CustomAPITestCase


class ContractListTests(CustomAPITestCase):
    contract_list_url = reverse('crm:contract_list')

    # --- Managers ---
    def test_manager_get_contract_list(self):
        """Managers can view all contracts in database"""
        user = User.objects.get(username='test_manager')
        test_client = self.get_token_auth_client(user)
        response = test_client.get(self.contract_list_url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), len(Contract.objects.all()))

    def test_manager_create_contract(self):
        """Managers must create clients via admin site"""
        user = User.objects.get(username='test_manager')
        test_client = self.get_token_auth_client(user)
        data = {
            'client': 1,
            'amount': 1234.56,
            'payment_due': '2022-10-09',
            'status': False
        }
        response = test_client.post(self.contract_list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # --- Sales ---
    def test_sales_get_contract_list(self):
        """Sales can view their own contracts"""
        user = User.objects.get(username='test_sales')
        test_client = self.get_token_auth_client(user)
        response = test_client.get(self.contract_list_url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for item in response.data:
            self.assertEqual(item['sales_contact'], user.id)

    def test_sales_create_contract(self):
        """Sales can create a new contract for a client
        Check if user is client's sales_contact
        """
        user = User.objects.get(username='test_sales')
        test_client = self.get_token_auth_client(user)
        data = {
            'client': 1,
            'amount': 1234.56,
            'payment_due': '2022-10-09',
            'status': False
        }
        response = test_client.post(self.contract_list_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(user, Client.objects.get(id=response.data['client']).sales_contact)
        self.assertEqual(user.id, response.data['sales_contact'])

    def test_sales_create_contract_unconverted_client(self):
        """Sales not allowed to create contract for unconverted client"""
        user = User.objects.get(username='test_sales')
        test_client = self.get_token_auth_client(user)
        data = {
            'client': 3,
            'amount': 1234.56,
            'payment_due': '2022-10-09',
            'status': False
        }
        response = test_client.post(self.contract_list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_contract_incomplete_data(self):
        """Check validation for missing fields in request"""
        user = User.objects.get(username='test_sales')
        test_client = self.get_token_auth_client(user)
        response = test_client.post(self.contract_list_url, data={'amount': 10}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # --- Support ---
    def test_support_get_contract_list(self):
        """Support can view their own contracts (support_contact)"""
        user = User.objects.get(username='test_support')
        test_client = self.get_token_auth_client(user)
        response = test_client.get(self.contract_list_url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for item in response.data:
            contract = Contract.objects.get(id=item['id'])
            self.assertIn(contract, Contract.objects.filter(event__support_contact=user.id))

    def test_support_create_contract(self):
        """Support not allowed to create a contract"""
        user = User.objects.get(username='test_support')
        test_client = self.get_token_auth_client(user)
        data = {
            'client': 1,
            'amount': 1234.56,
            'payment_due': '2022-10-09',
            'status': False
        }
        response = test_client.post(self.contract_list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class ContractDetailTests(CustomAPITestCase):

    # --- Managers ---
    def test_manager_get_contract_detail(self):
        """Managers can view any contract in database"""
        user = User.objects.get(username='test_manager')
        test_client = self.get_token_auth_client(user)
        id_list = self.get_id_list(Contract.objects.all())

        for i in range(len(id_list)):
            response = test_client.get(reverse('crm:contract_detail', kwargs={'pk': id_list[i]}))
            self.assertEqual(response.status_code, status.HTTP_200_OK)

    # --- Sales ---
    def test_sales_get_contract_detail(self):
        """Sales can view their own contract"""
        user = User.objects.get(username='test_sales')
        test_client = self.get_token_auth_client(user)
        id_list = self.get_id_list(Contract.objects.all())

        for i in range(len(id_list)):
            response = test_client.get(reverse('crm:contract_detail', kwargs={'pk': id_list[i]}))
            if Contract.objects.get(id=id_list[i]).sales_contact != user:
                self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
            else:
                self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_sales_update_contract(self):
        """Sales can update a contract if not signed"""
        user = User.objects.get(username='test_sales')
        test_client = self.get_token_auth_client(user)
        data = {
            'client': 2,
            'amount': 5432.10,
            'payment_due': '2022-10-09',
            'status': False
        }
        response = test_client.put('/crm/contracts/2/', data)

        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertEqual(5432.10, response.data['amount'])

    def test_sales_update_signed_contract(self):
        """Sales not allowed to update contract if signed"""
        user = User.objects.get(username='test_sales')
        test_client = self.get_token_auth_client(user)
        data = {
            'client': 1,
            'amount': 123.45,
            'payment_due': '2022-10-09',
            'status': True
        }
        response = test_client.put('/crm/contracts/3/', data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.json(), {"detail": "Cannot update a signed contract."})

    def test_update_contract_incomplete_data(self):
        """Check validation for missing fields in request"""
        user = User.objects.get(username='test_sales')
        test_client = self.get_token_auth_client(user)
        response = test_client.put('/crm/contracts/2/', data={'amount': 10})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # --- Support ---
    def test_support_get_contract_detail(self):
        """Support can only view their own contract (support_contact)"""
        user = User.objects.get(username='test_support')
        test_client = self.get_token_auth_client(user)

        response = test_client.get(reverse('crm:contract_detail', kwargs={'pk': 1}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = test_client.get(reverse('crm:contract_detail', kwargs={'pk': 2}))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_support_update_contract(self):
        """Support not allowed to update contract"""
        user = User.objects.get(username='test_support')
        test_client = self.get_token_auth_client(user)
        data = {
            'client': 2,
            'amount': 5432.10,
            'payment_due': '2022-10-09',
            'status': False
        }
        response = test_client.put('/crm/contracts/2/', data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
