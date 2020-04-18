from decimal import Decimal
from unittest.case import TestCase

from eventsourcing.application.notificationlog import NotificationLogReader
from eventsourcing.application.popo import PopoApplication

from invoicing.application import InvoicingApplication
from invoicing.domainmodel import Invoice


class TestInvoicing(TestCase):
    def test(self):
        with InvoicingApplication.mixin(PopoApplication)() as app:
            assert isinstance(app, InvoicingApplication)

            # Create an invoice.
            app.create_invoice(number="0001", amount=Decimal("10.00"))

            # Get invoice from repository.
            invoice = app.get_invoice("0001")
            self.assertIsInstance(invoice, Invoice)

            # Create an invoice.
            app.create_invoice(number="0002", amount=Decimal("10.00"))

            # Create an invoice.
            app.create_invoice(number="0003", amount=Decimal("10.00"))

            # Create an invoice.
            app.create_invoice(number="0004", amount=Decimal("10.00"))

            reader = NotificationLogReader(app.notification_log)
            event_notifications = reader.read_list()

            events = [
                app.event_store.event_mapper.event_from_topic_and_state(e["topic"], e["state"])
                for e in event_notifications
            ]

            total_amount_invoiced = sum([e.amount for e in events])
            self.assertEqual(total_amount_invoiced, Decimal("40.00"))
