from dataclasses import dataclass
from functools import total_ordering


@total_ordering
@dataclass
class LineItem:
    name: str
    quantity: int

    def __str__(self):
        return f"{self.quantity}x {self.name}"

    def __lt__(self, other):
        return self.name < other.name

    @classmethod
    def of(cls, raw) -> "LineItem":
        return LineItem(
            name=raw.name,
            quantity=raw.quantity,
        )
