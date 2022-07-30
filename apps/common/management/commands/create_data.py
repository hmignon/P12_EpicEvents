from django.core.management import BaseCommand, call_command


class Command(BaseCommand):
    help = "Create dummy data."

    def handle(self, *args, **options):
        call_command('create_users', number=15, verbosity=options["verbosity"])
        call_command('create_clients', number=50, verbosity=options["verbosity"])
        call_command('create_contracts', number=20, verbosity=options["verbosity"])
        call_command('create_events', number=10, verbosity=options["verbosity"])
