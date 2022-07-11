from django.conf import settings
from django.db import models

from apps.clients.models import Client


class Contract(models.Model):
    sales_contact = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        limit_choices_to={'team_id': 2}
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
    payment_due = models.DateField()

    def __str__(self):
        name = f"{self.client.last_name}, {self.client.first_name}"
        if self.status is False:
            stat = "NOT SIGNED"
        else:
            stat = "SIGNED"

        return f"Contract #{self.id} : {name} ({stat})"
