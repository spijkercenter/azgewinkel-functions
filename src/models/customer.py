from dataclasses import dataclass
from functools import total_ordering


@total_ordering
@dataclass
class Customer:
    id: int
    shortname: str
    name: str

    @classmethod
    def of(cls, raw) -> "Customer":
        return Customer(
            id=raw.id,
            shortname=raw.username,
            name=f"{raw.first_name} {raw.last_name}",
        )

    def __lt__(self, other):
        return self.shortname < other.shortname

    def __hash__(self):
        return self.id
