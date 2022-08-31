from datetime import datetime
from random import choice, randint

import pytz
from django.core.management import BaseCommand
from faker import Faker

from apps.contracts.models import Contract
from apps.events.models import Event
from apps.users.models import User


class Command(BaseCommand):
    help = "Create sample events data."

    def add_arguments(self, parser):
        parser.add_argument(
            "--number",
            "-n",
            dest="number",
            default=10,
            type=int,
            help="Specify the number of events to create.",
        )

    def handle(self, *args, **options):
        fake = Faker()
        number = options["number"]
        contracts = Contract.objects.filter(status=True).values_list("pk", flat=True)

        if contracts.count() < number:
            number = contracts.count()
            if options["verbosity"] != 0:
                self.stdout.write(f"Maximum events possible: {contracts.count()}")
        if options["verbosity"] != 0:
            self.stdout.write(f"Creating {number} event(s)...")
        self.create_events(fake, number, contracts)

    @staticmethod
    def create_events(fake, number, contracts):
        support_contacts = User.objects.filter(team_id=3).values_list("pk", flat=True)

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
            support = (
                choice(support_contacts)
                if choice([0, 1]) == 0 or status is True
                else None
            )

            Event.objects.create(
                contract_id=contract,
                name=name,
                location=f"{fake.street_address()}, {fake.city()}",
                support_contact_id=support,
                event_status=status,
                attendees=randint(5, 500),
                event_date=date,
                notes=fake.paragraph(nb_sentences=randint(2, 6)),
            )
