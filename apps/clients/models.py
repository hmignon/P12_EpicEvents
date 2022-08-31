from django.conf import settings
from django.db import models


class Client(models.Model):
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.EmailField()
    phone = models.CharField(max_length=30, blank=True, null=True)
    mobile = models.CharField(max_length=30, blank=True, null=True)
    company_name = models.CharField(max_length=250, blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    sales_contact = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={"team_id": 2},
    )
    status = models.BooleanField(default=False, verbose_name="Converted")

    def __str__(self):
        if self.status is False:
            stat = "PROSPECT"
        else:
            stat = "CONVERTED"
        return f"Client #{self.id} : {self.last_name}, {self.first_name} ({stat})"
