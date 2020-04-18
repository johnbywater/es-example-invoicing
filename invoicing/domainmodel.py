from eventsourcing.domain.model.aggregate import BaseAggregateRoot


class Invoice(BaseAggregateRoot):
    __subclassevents__ = True

    def __init__(self, amount, **kwargs):
        super(Invoice, self).__init__(**kwargs)
        self.amount = amount