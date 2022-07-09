from apps.common.tests.setup import CustomCRMTestCase
from apps.crm.models import Client, Contract, Event


class ModelsTests(CustomCRMTestCase):
    def test_str_client(self):
        client = Client.objects.get(id=1)
        self.assertEqual(str(client), "Client #1 : Miller, James (CONVERTED)")
        client = Client.objects.get(id=3)
        self.assertEqual(str(client), "Client #3 : Smith, John (PROSPECT)")

    def test_str_contract(self):
        contract = Contract.objects.get(id=1)
        self.assertEqual(str(contract), "Contract #1 : Miller, James (SIGNED)")
        contract = Contract.objects.get(id=2)
        self.assertEqual(str(contract), "Contract #2 : Dupont, Jean (NOT SIGNED)")

    def test_str_event(self):
        event = Event.objects.get(id=1)
        self.assertEqual(str(event), "Event #1 : Miller, James | Date : 2022-03-06 (UPCOMING)")
        event = Event.objects.get(id=3)
        self.assertEqual(str(event), "Event #3 : Dupont, Jean | Date : 2022-11-17 (COMPLETED)")
