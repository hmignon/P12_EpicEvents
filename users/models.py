from django.contrib.auth.models import AbstractUser, Group
from django.db import models


class User(AbstractUser):
    phone = models.CharField(max_length=20, blank=True, null=True)
