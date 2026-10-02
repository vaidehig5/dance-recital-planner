from dataclasses import dataclass, field


@dataclass
class Dance:
    """One dance in the recital."""

    id: int  # order among the dances in the uploaded file (1 = first)
    name: str
    dancer_ids: list[int] = field(default_factory=list)
    duration_seconds: int | None = None  # entered by the user later
    style: str | None = None  # optional, entered by the user later