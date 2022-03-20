from django.urls import reverse
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.test import APITestCase
from rest_framework_simplejwt.exceptions import AuthenticationFailed

from .models import User

TEST_PASSWORD = 'test_password'
LOGIN_URL = reverse('login')
UPDATE_PASSWORD_URL = reverse('update-password')


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
        self.assertRaises(AuthenticationFailed, msg='No active account found with the given credentials')

    def test_login_wrong_password(self):
        user = User.objects.get(username='test_user')
        data = {
            'username': user.username,
            'password': 'random_password',
        }
        response = self.client.post(LOGIN_URL, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertRaises(AuthenticationFailed, msg='No active account found with the given credentials')


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
        self.assertRaises(ValidationError, msg="Old password is not correct.")

    def test_non_identical_new_passwords(self):
        client = self.get_token_auth_client()
        data = {
            'old_password': TEST_PASSWORD,
            'password': 'new_password',
            'password2': 'different_password',
        }
        response = client.put(UPDATE_PASSWORD_URL, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertRaises(ValidationError, msg="Password fields didn't match.")
