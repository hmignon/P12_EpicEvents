from crm.models import Client, Contract, Event
from .setup import CustomAPITestCase


class ModelsTests(CustomAPITestCase):
    def test_str_client(self):
        client = Client.objects.get(id=1)
        self.assertEqual(str(client), "Client #1 : Miller, James (CONVERTED)")
        client = Client.objects.get(id=3)
        self.assertEqual(str(client), "Client #3 : Smith, John (PROSPECT)")

    def test_str_contract(self):
        contract = Contract.objects.get(id=1)
        self.assertEqual(str(contract), "Contract #1 : Miller, James | Due : 2022-02-27 (SIGNED)")
        contract = Contract.objects.get(id=2)
        self.assertEqual(str(contract), "Contract #2 : Dupont, Jean | Due : 2022-04-13 (NOT SIGNED)")

    def test_str_event(self):
        event = Event.objects.get(id=1)
        self.assertEqual(str(event), "Event #1 : Miller, James | Date : 2022-03-06 (UPCOMING)")
        event = Event.objects.get(id=3)
        self.assertEqual(str(event), "Event #3 : Dupont, Jean | Date : 2022-11-17 (COMPLETED)")
