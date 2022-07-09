from django.core.management import call_command
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from apps.crm.models import Contract
from apps.users.models import User

TEST_PASSWORD = 'test_password'
LOGIN_URL = reverse('users:login')


class CustomCRMTestCase(APITestCase):
    """
    Custom API test case for CRM tests.
    Adds common setUp method to load data.
    """

    def setUp(self):
        """
        Create test users with hashed passwords.
        Load initial data from fixtures/data.json.
        """
        User.objects.create_user(
            id=1,
            username='test_manager',
            password=TEST_PASSWORD,
            email='test_manager@email.com',
            team_id=1
        )
        User.objects.create_user(
            id=2,
            username='test_sales',
            password=TEST_PASSWORD,
            email='test_sales@email.com',
            team_id=2
        )
        User.objects.create_user(
            id=3,
            username='test_support',
            password=TEST_PASSWORD,
            email='test_support@email.com',
            team_id=3
        )

        call_command('loaddata', 'apps/common/fixtures/data.json', verbosity=0)

    def get_token_auth_client(self, user):
        """
        User token authentication.
        Returns APIClient with JWT authorization for current user.
        """
        data = {
            'username': user.username,
            'password': TEST_PASSWORD,
        }
        response = self.client.post(LOGIN_URL, data, format='json')
        token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

        return self.client

    @staticmethod
    def get_id_list(queryset):
        """
        Returns list of available ids in current queryset.
        """
        id_list = []
        for i in range(len(queryset)):
            id_list.append(queryset[i].id)

        return id_list

    @staticmethod
    def create_contract():
        contract = Contract.objects.create(client_id=1, amount=123.45, payment_due='2022-06-09', status=True)
        return contract
