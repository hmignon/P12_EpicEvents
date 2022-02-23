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
    status = models.CharField(
        choices=[
            ('POTENTIAL', 'POTENTIAL'),
            ('EXISTING', 'EXISTING'),
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
        due = self.payment_due.strftime('%Y-%m-%d')
        if self.status is False:
            stat = "NOT SIGNED"
        else:
            stat = "SIGNED"

        return f"Contract #{self.id} : {self.client.last_name}, {self.client.first_name} | Due : {due} ({stat})"


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
        date = self.event_date.strftime('%Y-%m-%d')
        if self.event_status is False:
            stat = "UPCOMING"
        else:
            stat = "FINISHED"

        return f"Event #{self.id} : {self.client.last_name}, {self.client.first_name} | Date : {date} ({stat})"
