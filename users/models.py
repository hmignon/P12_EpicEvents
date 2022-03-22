from django.contrib.auth.models import AbstractUser
from django.db import models

MANAGEMENT = 'MANAGEMENT'
SALES = 'SALES'
SUPPORT = 'SUPPORT'


class User(AbstractUser):
    phone = models.CharField(max_length=20, blank=True, null=True)
    mobile = models.CharField(max_length=20, blank=True, null=True)
    team = models.CharField(
        choices=[
            (MANAGEMENT, MANAGEMENT),
            (SALES, SALES),
            (SUPPORT, SUPPORT)
        ],
        max_length=10,
        default=MANAGEMENT
    )

    def __str__(self):
        return f"{self.username} ({self.team})"

    def save(self, *args, **kwargs):
        if self.team == MANAGEMENT:
            self.is_superuser = True
            self.is_staff = True
        else:
            self.is_superuser = False
            self.is_staff = False

        user = super(User, self)
        user.save()

        return user
