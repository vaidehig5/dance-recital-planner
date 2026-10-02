from dataclasses import dataclass, field


@dataclass
class Dancer:
    """One person who performs in one or more dances."""

    id: int  # assigned in the order dancers are first seen
    name: str  # displayed using the first spelling found in the spreadsheet
    dance_ids: list[int] = field(default_factory=list)