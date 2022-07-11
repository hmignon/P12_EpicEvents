from django.conf import settings
from django.db import models

from apps.contracts.models import Contract


class Event(models.Model):
    contract = models.OneToOneField(
        to=Contract,
        on_delete=models.CASCADE,
        limit_choices_to={'status': True},
        related_name='event'
    )
    name = models.CharField(max_length=100, null=True, blank=True)
    location = models.CharField(max_length=200, null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    support_contact = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        limit_choices_to={'team_id': 3}
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
