from dataclasses import dataclass, field


@dataclass
class ValidationIssue:
    """One message for the user, optionally tied to a spreadsheet column."""

    message: str
    column_number: int | None = None


@dataclass
class ValidationResult:
    """Everything found while checking a spreadsheet.

    Errors block the show order from being generated. Warnings are shown
    but don't block anything.
    """

    errors: list[ValidationIssue] = field(default_factory=list)
    warnings: list[ValidationIssue] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        return not self.errors