from django.conf import settings
from django.db import models


class Client(models.Model):
    first_name = models.CharField(max_length=25)
    last_name = models.CharField(max_length=25)
    email = models.EmailField(max_length=100)
    phone = models.CharField(max_length=20, blank=True, null=True)
    mobile = models.CharField(max_length=20, blank=True, null=True)
    company_name = models.CharField(max_length=250, blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    sales_contact = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        limit_choices_to={'team': 'SALES'}
    )
    status = models.BooleanField(default=False, verbose_name="Converted")

    def __str__(self):
        if self.status is False:
            stat = "PROSPECT"
        else:
            stat = "CONVERTED"
        return f"Client #{self.id} : {self.last_name}, {self.first_name} ({stat})"


class Contract(models.Model):
    sales_contact = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        limit_choices_to={'team': 'SALES'}
    )
    client = models.ForeignKey(
        to=Client,
        on_delete=models.CASCADE,
        limit_choices_to={'status': True},
        related_name='contract'
    )
    status = models.BooleanField(default=False, verbose_name="Signed")
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    amount = models.FloatField()
    payment_due = models.DateTimeField()

    def __str__(self):
        name = f"{self.client.last_name}, {self.client.first_name}"
        due = self.payment_due.strftime('%Y-%m-%d')
        if self.status is False:
            stat = "NOT SIGNED"
        else:
            stat = "SIGNED"

        return f"Contract #{self.id} : {name} | Due : {due} ({stat})"


class Event(models.Model):
    contract = models.OneToOneField(
        to=Contract,
        on_delete=models.CASCADE,
        limit_choices_to={'status': True},
        related_name='event'
    )
    name = models.CharField(max_length=100, null=True, blank=True)
    location = models.CharField(max_length=100, null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    support_contact = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        limit_choices_to={'team': 'SUPPORT'}
    )
    event_status = models.BooleanField(default=False, verbose_name="Completed")
    attendees = models.PositiveIntegerField()
    event_date = models.DateTimeField()
    notes = models.TextField(null=True, blank=True)

    def __str__(self):
        name = f"{self.contract.client.last_name}, {self.contract.client.first_name}"
        date = self.event_date.strftime('%Y-%m-%d')
        if self.event_status is False:
            stat = "UPCOMING"
        else:
            stat = "COMPLETED"

        return f"Event #{self.id} : {name} | Date : {date} ({stat})"
