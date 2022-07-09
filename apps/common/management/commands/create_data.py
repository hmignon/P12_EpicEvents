from django.core import management
from django.core.management import BaseCommand


class Command(BaseCommand):

    help = "Create dummy data."

    def handle(self, *args, **options):
        management.call_command('create_users', number=15)
        management.call_command('create_clients', number=50)
        management.call_command('create_contracts', number=20)
        management.call_command('create_events', number=10)
