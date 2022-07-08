from datetime import datetime
from random import choice, randint

import pytz
from django.core.management import BaseCommand
from faker import Faker

from apps.crm.models import Contract, Event
from apps.users.models import User


class Command(BaseCommand):
    help = "Create sample events data."

    def add_arguments(self, parser):
        parser.add_argument(
            '--number',
            '-n',
            dest='number',
            default=20,
            type=int,
            help="Specify the number of events to create.",
        )

    def handle(self, *args, **options):
        fake = Faker()
        number = options["number"]
        self.stdout.write(f"Creating {number} events...")
        self.create_events(fake, number)

    def create_events(self, fake, number):
        support_contacts = User.objects.filter(team_id=3).values_list('pk', flat=True)
        contracts = Contract.objects.filter(status=True).values_list('pk', flat=True)

        if contracts.count() < number:
            self.stdout.write(f"Maximum events possible: {contracts.count()}")
            number = contracts.count()

        for _ in range(number):
            contract = choice(contracts)
            while Event.objects.filter(contract_id=contract).exists():
                contract = choice(contracts)

            name = ""
            for j in range(randint(2, 5)):
                name = f"{name} {fake.word().title()}"

            date = fake.date_time_between_dates(
                datetime_start=datetime(2022, 1, 1, 0, 0, 0, tzinfo=pytz.UTC),
                datetime_end=datetime(2023, 12, 31, 23, 59, 59, tzinfo=pytz.UTC),
                tzinfo=pytz.UTC,
            )
            status = True if date < datetime.now(tz=pytz.UTC) else False
            support = choice(support_contacts) if choice([0, 1]) == 0 or status is True else None

            Event.objects.create(
                contract_id=contract,
                name=name,
                location=fake.address(),
                support_contact_id=support,
                event_status=status,
                attendees=randint(5, 1000),
                event_date=date,
                notes=fake.paragraph(nb_sentences=randint(2, 6)),
            )
