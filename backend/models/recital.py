from dataclasses import dataclass, field

from backend.models.dance import Dance
from backend.models.dancer import Dancer


@dataclass
class Recital:
    """All dances and dancers from one uploaded spreadsheet."""

    dances: list[Dance] = field(default_factory=list)  # in the original upload order
    dancers: list[Dancer] = field(default_factory=list)  # in the order first seen