from datetime import datetime
from random import choice

from django.core.management import BaseCommand
from faker import Faker

from apps.clients.models import Client
from apps.contracts.models import Contract


class Command(BaseCommand):
    help = "Create sample contracts data."

    def add_arguments(self, parser):
        parser.add_argument(
            '--number',
            '-n',
            dest='number',
            default=20,
            type=int,
            help="Specify the number of contracts to create.",
        )

    def handle(self, *args, **options):
        fake = Faker()
        number = options["number"]
        self.stdout.write(f"Creating {number} contracts...")
        self.create_contracts(fake, number)

    @staticmethod
    def create_contracts(fake, number):
        clients = Client.objects.filter(status=True).values_list('pk', flat=True)

        for _ in range(number):
            client = choice(clients)
            Contract.objects.create(
                client_id=client,
                sales_contact=Client.objects.get(id=client).sales_contact,
                status=fake.boolean(chance_of_getting_true=70),
                amount=fake.pyfloat(right_digits=2, positive=True, min_value=100, max_value=99999),
                payment_due=fake.date_between_dates(
                    date_start=datetime(2022, 1, 1),
                    date_end=datetime(2023, 12, 31)
                ).strftime('%Y-%m-%d'),
            )
