from django.urls import reverse
from rest_framework import status
from rest_framework.exceptions import PermissionDenied

from apps.common.tests.setup import CommandTestCase, CustomCRMTestCase, TEST_PASSWORD
from .models import Team, User

USER_COMMAND = "create_users"


class UserCommandTests(CommandTestCase):
    def test_create_users_default(self):
        """Create users command, default number: 15.
        Check created data types and validity."""
        users_before = User.objects.all().count()
        out = self.call_command(USER_COMMAND)
        self.assertEqual(out, "Creating 15 user(s)...\n")
        self.assertEqual(User.objects.all().count(), users_before + 15)

        # test created data
        users = User.objects.all().order_by("-id")[:15]
        for user in users:
            self.assertEqual(type(user.first_name), str)
            self.assertEqual(type(user.last_name), str)
            self.assertEqual(type(user.username), str)
            self.assertEqual(type(user.password), str)
            self.assertEqual(type(user.email), str)
            self.assertEqual(type(user.phone), str)
            self.assertEqual(type(user.mobile), str)
            self.assertEqual(type(user.team_id), int)
            self.assertIn(user.team_id, [1, 2, 3])

    def test_create_users_with_args(self):
        """Create users command with number args."""
        users_before = User.objects.all().count()
        out = self.call_command(USER_COMMAND, "-n 12")
        self.assertEqual(out, "Creating 12 user(s)...\n")
        self.assertEqual(User.objects.all().count(), users_before + 12)

        users_before = User.objects.all().count()
        out = self.call_command(USER_COMMAND, "--number=8")
        self.assertEqual(out, "Creating 8 user(s)...\n")
        self.assertEqual(User.objects.all().count(), users_before + 8)


class LoginTests(CustomCRMTestCase):
    login_url = reverse("users:login")

    def test_login_valid_credentials(self):
        """Valid login returns JWT tokens."""
        user = User.objects.get(username="test_sales")
        data = {
            "username": user.username,
            "password": TEST_PASSWORD,
        }
        response = self.client.post(self.login_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_login_unknown_username(self):
        """Invalid username returns error message."""
        data = {
            "username": "random_username",
            "password": TEST_PASSWORD,
        }
        response = self.client.post(self.login_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(
            response.json(),
            {"detail": "No active account found with the given credentials"},
        )

    def test_login_wrong_password(self):
        """Invalid password returns error message."""
        user = User.objects.get(username="test_sales")
        data = {
            "username": user.username,
            "password": "random_password",
        }
        response = self.client.post(self.login_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(
            response.json(),
            {"detail": "No active account found with the given credentials"},
        )


class UpdatePasswordTests(CustomCRMTestCase):
    update_password_url = reverse("users:update_password")

    def test_change_password_ok(self):
        """Valid password update returns 200 status code."""
        user = User.objects.get(username="test_sales")
        client = self.get_token_auth_client(user)
        data = {
            "old_password": TEST_PASSWORD,
            "password": "new_password",
            "password2": "new_password",
        }
        response = client.put(self.update_password_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_invalid_old_password(self):
        """Invalid old password returns error message."""
        user = User.objects.get(username="test_sales")
        client = self.get_token_auth_client(user)
        data = {
            "old_password": "wrong_password",
            "password": "new_password",
            "password2": "new_password",
        }
        response = client.put(self.update_password_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.json(),
            {"old_password": {"old_password": "Old password is not correct."}},
        )

    def test_non_identical_new_passwords(self):
        """Non identical passwords update returns error message."""
        user = User.objects.get(username="test_sales")
        client = self.get_token_auth_client(user)
        data = {
            "old_password": TEST_PASSWORD,
            "password": "new_password",
            "password2": "different_password",
        }
        response = client.put(self.update_password_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.json(), {"password": ["Password fields didn't match."]}
        )


class TeamModelTests(CustomCRMTestCase):
    def test_str_team(self):
        self.assertEqual(str(Team.objects.get(id=1)), "MANAGEMENT")
        self.assertEqual(str(Team.objects.get(id=2)), "SALES")
        self.assertEqual(str(Team.objects.get(id=3)), "SUPPORT")

    def test_three_teams(self):
        self.assertEqual(len(Team.objects.all()), 3)

    def test_create_team(self):
        with self.assertRaisesMessage(
            PermissionDenied, "You are not permitted to create or edit teams."
        ):
            Team.objects.create(name="Test")

    def test_update_team(self):
        team = Team.objects.get(id=1)
        team.name = "Test"
        with self.assertRaisesMessage(
            PermissionDenied, "You are not permitted to create or edit teams."
        ):
            team.save()

    def test_delete_team(self):
        team = Team.objects.get(id=1)
        with self.assertRaisesMessage(
            PermissionDenied, "You are not permitted to delete teams."
        ):
            team.delete()


class UserModelTests(CustomCRMTestCase):
    def test_str_user(self):
        self.assertEqual(str(User.objects.get(id=1)), "test_manager (MANAGEMENT)")
        self.assertEqual(str(User.objects.get(id=2)), "test_sales (SALES)")
        self.assertEqual(str(User.objects.get(id=3)), "test_support (SUPPORT)")

    def test_user_team_if_staff_or_superuser(self):
        """Superuser and staff status for managers only."""
        manager = User.objects.get(id=1)
        self.assertTrue(manager.is_staff)
        self.assertTrue(manager.is_superuser)

        sales = User.objects.get(id=2)
        self.assertFalse(sales.is_staff)
        self.assertFalse(sales.is_superuser)

        support = User.objects.get(id=3)
        self.assertFalse(support.is_staff)
        self.assertFalse(support.is_superuser)
