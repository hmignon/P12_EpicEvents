import datetime

from django.core.management import call_command
from rest_framework import status
from rest_framework.reverse import reverse

from apps.clients.models import Client
from apps.common.tests.setup import CommandTestCase, CustomCRMTestCase
from apps.users.models import User
from .models import Contract

CONTRACT_COMMAND = "create_contracts"


class ContractCommandTests(CommandTestCase):

    @staticmethod
    def create_sample_data():
        call_command("create_users", "--verbosity=0")
        call_command("create_clients", "--verbosity=0")

    def test_create_contracts_default(self):
        self.create_sample_data()
        clients = Client.objects.filter(status=True).count()
        contracts_before = Contract.objects.all().count()
        out = self.call_command(CONTRACT_COMMAND)
        if clients < 20:
            self.assertEqual(out, f"Maximum contracts possible: {clients}\nCreating {clients} contract(s)...\n")
            self.assertEqual(Contract.objects.all().count(), contracts_before + clients)
        else:
            self.assertEqual(out, "Creating 20 contract(s)...\n")
            self.assertEqual(Contract.objects.all().count(), contracts_before + 20)
            clients = 20

        # test created data
        contracts = Contract.objects.all().order_by('-id')[:clients]
        for contract in contracts:
            self.assertEqual(type(contract.client_id), int)
            self.assertEqual(type(contract.sales_contact_id), int)
            self.assertEqual(contract.sales_contact_id, contract.client.sales_contact_id)
            self.assertEqual(contract.sales_contact.team_id, 2)
            self.assertEqual(type(contract.status), bool)
            self.assertEqual(type(contract.amount), float)
            self.assertEqual(type(contract.payment_due), datetime.date)

    def test_create_contracts_with_args(self):
        self.create_sample_data()
        contracts_before = Contract.objects.all().count()
        out = self.call_command(CONTRACT_COMMAND, "-n 12")
        self.assertEqual(out, "Creating 12 contract(s)...\n")
        self.assertEqual(Contract.objects.all().count(), contracts_before + 12)

        contracts_before = Contract.objects.all().count()
        out = self.call_command(CONTRACT_COMMAND, "--number=8")
        self.assertEqual(out, "Creating 8 contract(s)...\n")
        self.assertEqual(Contract.objects.all().count(), contracts_before + 8)


class ContractListTests(CustomCRMTestCase):
    contract_list_url = reverse('contracts:list')
    contract_create_data = {
        'client': 1,
        'amount': 1234.56,
        'payment_due': '2022-10-09',
        'status': False
    }

    # --- Managers ---
    def test_manager_get_contract_list(self):
        """Managers can view all contracts in database."""
        user = User.objects.get(username='test_manager')
        test_client = self.get_token_auth_client(user)
        response = test_client.get(self.contract_list_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), len(Contract.objects.all()))

    def test_manager_create_contract(self):
        """Managers must create contracts via admin site."""
        user = User.objects.get(username='test_manager')
        test_client = self.get_token_auth_client(user)
        response = test_client.post(self.contract_list_url, self.contract_create_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # --- Sales ---
    def test_sales_get_contract_list(self):
        """Sales can view their own contracts."""
        user = User.objects.get(username='test_sales')
        test_client = self.get_token_auth_client(user)
        response = test_client.get(self.contract_list_url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for item in response.data:
            self.assertEqual(item['sales_contact'], user.id)

    def test_sales_create_contract(self):
        """Sales can create a new contract for a client.
        Check if user is client's and contract's sales_contact.
        """
        user = User.objects.get(username='test_sales')
        test_client = self.get_token_auth_client(user)
        response = test_client.post(self.contract_list_url, self.contract_create_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(user, Client.objects.get(id=response.data['client']).sales_contact)
        self.assertEqual(user.id, response.data['sales_contact'])

    def test_sales_create_contract_unconverted_client(self):
        """Sales not allowed to create contract for unconverted client."""
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
        """Check validation for missing fields in request."""
        user = User.objects.get(username='test_sales')
        test_client = self.get_token_auth_client(user)
        response = test_client.post(self.contract_list_url, data={'amount': 10}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # --- Support ---
    def test_support_get_contract_list(self):
        """Support can view their own contracts (support_contact)."""
        user = User.objects.get(username='test_support')
        test_client = self.get_token_auth_client(user)
        response = test_client.get(self.contract_list_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for item in response.data:
            contract = Contract.objects.get(id=item['id'])
            self.assertIn(contract, Contract.objects.filter(event__support_contact=user.id))

    def test_support_create_contract(self):
        """Support not allowed to create a contract."""
        user = User.objects.get(username='test_support')
        test_client = self.get_token_auth_client(user)
        response = test_client.post(self.contract_list_url, self.contract_create_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class ContractDetailTests(CustomCRMTestCase):
    contract_detail_url = 'contracts:detail'
    contract_update_data = {
        'client': 2,
        'amount': 5432.10,
        'payment_due': '2022-10-09',
        'status': False
    }

    # --- Managers ---
    def test_manager_get_contract_detail(self):
        """Managers can view any contract in database."""
        user = User.objects.get(username='test_manager')
        test_client = self.get_token_auth_client(user)
        for contract_id in self.get_id_list(Contract.objects.all()):
            response = test_client.get(reverse(self.contract_detail_url, kwargs={'pk': contract_id}))
            self.assertEqual(response.status_code, status.HTTP_200_OK)

    # --- Sales ---
    def test_sales_get_contract_detail(self):
        """Sales can view their own contract."""
        user = User.objects.get(username='test_sales')
        test_client = self.get_token_auth_client(user)
        for contract_id in self.get_id_list(Contract.objects.all()):
            response = test_client.get(reverse(self.contract_detail_url, kwargs={'pk': contract_id}))
            if Contract.objects.get(id=contract_id).sales_contact != user:
                self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
            else:
                self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_sales_update_contract(self):
        """Sales can update a contract if not signed."""
        user = User.objects.get(username='test_sales')
        test_client = self.get_token_auth_client(user)
        response = test_client.put('/crm/contracts/2/', self.contract_update_data)
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertEqual(5432.10, response.data['amount'])

    def test_sales_update_signed_contract(self):
        """Sales not allowed to update contract if signed."""
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
        """Check validation for missing fields in request."""
        user = User.objects.get(username='test_sales')
        test_client = self.get_token_auth_client(user)
        response = test_client.put('/crm/contracts/2/', data={'amount': 10})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # --- Support ---
    def test_support_get_contract_detail(self):
        """Support can only view their own contract (support_contact)."""
        user = User.objects.get(username='test_support')
        test_client = self.get_token_auth_client(user)
        response1 = test_client.get(reverse(self.contract_detail_url, kwargs={'pk': 1}))
        response2 = test_client.get(reverse(self.contract_detail_url, kwargs={'pk': 2}))
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        self.assertEqual(response2.status_code, status.HTTP_403_FORBIDDEN)

    def test_support_update_contract(self):
        """Support not allowed to update contract."""
        user = User.objects.get(username='test_support')
        test_client = self.get_token_auth_client(user)
        response = test_client.put('/crm/contracts/2/', self.contract_update_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class ContractModelTests(CustomCRMTestCase):

    def test_str_contract(self):
        contract = Contract.objects.get(id=1)
        self.assertEqual(str(contract), "Contract #1 : Miller, James (SIGNED)")
        contract = Contract.objects.get(id=2)
        self.assertEqual(str(contract), "Contract #2 : Dupont, Jean (NOT SIGNED)")
