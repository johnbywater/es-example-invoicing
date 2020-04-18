from uuid import NAMESPACE_URL, UUID, uuid5

from eventsourcing.application.simple import SimpleApplication

from invoicing.domainmodel import Invoice


class InvoicingApplication(SimpleApplication):
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
