from decimal import Decimal
from unittest.case import TestCase
from uuid import NAMESPACE_URL, UUID, uuid5

from eventsourcing.application.notificationlog import NotificationLogReader
from eventsourcing.application.sqlalchemy import SQLAlchemyApplication
from eventsourcing.domain.model.aggregate import BaseAggregateRoot


class Invoice(BaseAggregateRoot):
    __subclassevents__ = True

    def __init__(self, amount, **kwargs):
        super(Invoice, self).__init__(**kwargs)
        self.amount = amount


class InvoicingApplication(SQLAlchemyApplication):
    persist_event_type = Invoice.Event

    def create_invoice(self, number, amount) -> UUID:
        invoice_id = self.create_invoice_id(number)
        invoice = Invoice.__create__(originator_id=invoice_id, amount=amount)
        invoice.__save__()
        return invoice.id

    def create_invoice_id(self, number):
        return uuid5(NAMESPACE_URL, "/invoices/%s" % number)

    def get_invoice(self, invoice_number):
        invoice_id = self.create_invoice_id(invoice_number)
        return self.repository[invoice_id]


class TestInvoicing(TestCase):
    def test(self):
        with InvoicingApplication() as app:
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
