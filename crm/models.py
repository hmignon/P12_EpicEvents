from django.conf import settings
from django.db import models


class Client(models.Model):
    first_name = models.CharField(max_length=25)
    last_name = models.CharField(max_length=25)
    email = models.EmailField(max_length=100)
    phone = models.CharField(max_length=20, blank=True, null=True)
    mobile = models.CharField(max_length=20, blank=True, null=True)
    company_name = models.CharField(max_length=250)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    sales_contact = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Contract(models.Model):
    sales_contact = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    client = models.ForeignKey(to=Client, on_delete=models.CASCADE)
    status = models.BooleanField(default=True)
    amount = models.FloatField()
    payment_due = models.DateTimeField()

    def __str__(self):
        return f"{self.client} | {self.sales_contact} | {self.status}"


class Event(models.Model):
    client = models.ForeignKey(to=Client, on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    support_contact = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    event_status = models.BooleanField(default=True)
    attendees = models.PositiveIntegerField()
    event_date = models.DateTimeField()
    notes = models.TextField()

    def __str__(self):
        return f"{self.event_date} ({self.event_status})"
