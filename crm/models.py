from django.conf import settings
from django.db import models

from datetime import datetime


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
    status = models.CharField(
        choices=[
            ('POTENTIAL', 'POTENTIAL'),
            ('CONVERTED', 'CONVERTED'),
            ('CONTRACT', 'CONTRACT')
        ],
        max_length=15,
        default='POTENTIAL'
    )

    def __str__(self):
        return f"Client #{self.id} : {self.last_name}, {self.first_name} ({self.status})"


class Contract(models.Model):
    sales_contact = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    client = models.ForeignKey(to=Client, on_delete=models.CASCADE)
    status = models.BooleanField(default=False, verbose_name="Signed")
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    amount = models.FloatField()
    payment_due = models.DateTimeField()

    def __str__(self):
        created = datetime.strptime(self.date_created, '%Y-%m-%d %H:%M:%S')
        if self.status is False:
            stat = "Not signed"
        else:
            stat = "Signed"

        return f"Contract #{self.id} : {self.client} - {created} ({stat})"


class Event(models.Model):
    client = models.ForeignKey(to=Client, on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    support_contact = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    event_status = models.BooleanField(default=False, verbose_name="Event finished")
    attendees = models.PositiveIntegerField()
    event_date = models.DateTimeField()
    notes = models.TextField()

    def __str__(self):
        date = datetime.strptime(self.event_date, '%Y-%m-%d %H:%M:%S')
        if self.event_status is False:
            stat = "Upcoming"
        else:
            stat = "Finished"

        return f"Event #{self.id} : {self.client} - {date} ({stat})"
