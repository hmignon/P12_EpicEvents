from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import User

TEST_PASSWORD = 'test_password'
LOGIN_URL = reverse('users:login')
UPDATE_PASSWORD_URL = reverse('users:update_password')


class LoginTests(APITestCase):
    def setUp(self):
        User.objects.create_user(username='test_user', password=TEST_PASSWORD, email='test_user@email.com')

    def test_login_valid_credentials(self):
        user = User.objects.get(username='test_user')
        data = {
            'username': user.username,
            'password': TEST_PASSWORD,
        }
        response = self.client.post(LOGIN_URL, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_login_unknown_username(self):
        data = {
            'username': 'random_username',
            'password': TEST_PASSWORD,
        }
        response = self.client.post(LOGIN_URL, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.json(), {"detail": 'No active account found with the given credentials'})

    def test_login_wrong_password(self):
        user = User.objects.get(username='test_user')
        data = {
            'username': user.username,
            'password': 'random_password',
        }
        response = self.client.post(LOGIN_URL, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.json(), {"detail": 'No active account found with the given credentials'})


class UpdatePasswordTests(APITestCase):
    def setUp(self):
        User.objects.create_user(username='test_user', password=TEST_PASSWORD, email='test_user@email.com')

    def get_token_auth_client(self):
        user = User.objects.get(username='test_user')
        data = {
            'username': user.username,
            'password': TEST_PASSWORD,
        }
        response = self.client.post(LOGIN_URL, data, format='json')
        token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        return self.client

    def test_change_password_ok(self):
        client = self.get_token_auth_client()
        data = {
            'old_password': TEST_PASSWORD,
            'password': 'new_password',
            'password2': 'new_password',
        }
        response = client.put(UPDATE_PASSWORD_URL, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_invalid_old_password(self):
        client = self.get_token_auth_client()
        data = {
            'old_password': 'wrong_password',
            'password': 'new_password',
            'password2': 'new_password',
        }
        response = client.put(UPDATE_PASSWORD_URL, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), {'old_password': {'old_password': 'Old password is not correct.'}})

    def test_non_identical_new_passwords(self):
        client = self.get_token_auth_client()
        data = {
            'old_password': TEST_PASSWORD,
            'password': 'new_password',
            'password2': 'different_password',
        }
        response = client.put(UPDATE_PASSWORD_URL, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), {"password": ["Password fields didn't match."]})


class UserModelTests(APITestCase):
    def setUp(self):
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

    def test_str_user(self):
        self.assertEqual(str(User.objects.get(id=1)), "test_manager (MANAGEMENT)")
        self.assertEqual(str(User.objects.get(id=2)), "test_sales (SALES)")
        self.assertEqual(str(User.objects.get(id=3)), "test_support (SUPPORT)")

    def test_user_team_if_staff_or_superuser(self):
        user = User.objects.get(id=1)
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)

        user = User.objects.get(id=2)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

        user = User.objects.get(id=3)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
