from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from functools import total_ordering
from typing import List, Dict

from .customer import Customer
from .line_item import LineItem

order_stati = {
    "fitting": "Te bestellen door lid",
    "pending": "Te betalen aan AZG",
    "paid": "Betaald aan AZG",
    "ordered": "Besteld bij Rasch",
    "completed": "Afgeleverd in ruimte"
}


@total_ordering
@dataclass
class Order:
    id: int
    date_created: datetime
    customer: Customer
    total: Decimal
    status: str
    human_status: str
    line_items: List[LineItem]

    def __eq__(self, other):
        return self.id == other.id

    def __lt__(self, other):
        return self.date_created < other.date_created

    def __str__(self):
        line_items = ", ".join([str(li) for li in self.line_items])
        return f"#{self.id}({self.status}) by {self.customer.name} for {self.total} with {line_items}"

    @classmethod
    def of(cls, raw, customers: Dict[int, Customer]) -> "Order":
        status = raw.status
        if status in order_stati.keys():
            status = order_stati[status]
        return Order(
            id=raw.id,
            date_created=raw.date_created,
            customer=Order.fallback_customer(raw.customer_id, customers),
            total=Decimal(raw.total),
            status=raw.status,
            human_status=status,
            line_items=sorted([LineItem.of(li) for li in raw.line_items])
        )

    @classmethod
    def fallback_customer(cls, customer_id: int, customers: Dict[int, Customer]) -> Customer:
        try:
            return customers[customer_id]
        except KeyError:
            return Customer(customer_id, "UNKNOWN")
