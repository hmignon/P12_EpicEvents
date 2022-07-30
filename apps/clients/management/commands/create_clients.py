from random import choice

from django.core.management import BaseCommand
from faker import Faker

from apps.clients.models import Client
from apps.users.models import User


class Command(BaseCommand):
    help = "Create sample clients data."

    def add_arguments(self, parser):
        parser.add_argument(
            '--number',
            '-n',
            dest='number',
            default=50,
            type=int,
            help="Specify the number of clients to create.",
        )

    def handle(self, *args, **options):
        fake = Faker()
        number = options["number"]
        if options["verbosity"] != 0:
            self.stdout.write(f"Creating {number} client(s)...")
        self.create_clients(fake, number)

    @staticmethod
    def create_clients(fake, number):
        sales = User.objects.filter(team_id=2).values_list('pk', flat=True)
        for _ in range(number):
            status = fake.pybool()
            if status:
                contact = choice(sales)
            else:
                contact = None

            Client.objects.create(
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                company_name=fake.company(),
                email=fake.ascii_safe_email(),
                phone=fake.phone_number(),
                mobile=fake.phone_number(),
                status=status,
                sales_contact_id=contact,
            )
