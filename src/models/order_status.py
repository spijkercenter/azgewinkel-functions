from dataclasses import dataclass
from functools import total_ordering
from typing import List


@total_ordering
@dataclass
class OrderStatus:
    id: int
    key: str
    name: str

    def __lt__(self, other):
        return self.id < other.id

    def __hash__(self):
        return self.id

    @staticmethod
    def all() -> List["OrderStatus"]:
        return [
            OrderStatus(1, "fitting", "Te bestellen door lid"),
            OrderStatus(2, "pending", "Te betalen aan AZG"),
            OrderStatus(3, "paid", "Te bestellen bij leverancier"),
            OrderStatus(4, "ordered", "Te leveren aan AZG"),
            OrderStatus(5, "completed", "Afgeleverd in ruimte")
        ]

    @staticmethod
    def of(key: str) -> "OrderStatus":
        matches = [os for os in OrderStatus.all() if os.key == key]
        if matches:
            return matches[0]
        else:
            return OrderStatus(-1, key, key)
