from random import randint

from django.core.management import BaseCommand
from faker import Faker

from apps.users.models import User


class Command(BaseCommand):
    help = "Create sample users."

    def add_arguments(self, parser):
        parser.add_argument(
            '--number',
            '-n',
            dest='number',
            default=15,
            type=int,
            help="Specify the number of users to create.",
        )

    def handle(self, *args, **options):
        fake = Faker()
        number = options["number"]
        if options["verbosity"] != 0:
            self.stdout.write(f"Creating {number} user(s)...")
        self.create_users(fake, number)

    @staticmethod
    def create_users(fake, number):
        for _ in range(number):
            User.objects.create_user(
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                username=f"{fake.user_name()}{randint(1, 99)}",
                password=fake.password(length=8),
                email=fake.ascii_safe_email(),
                phone=fake.phone_number(),
                mobile=fake.phone_number(),
                team_id=randint(1, 3),
            )
