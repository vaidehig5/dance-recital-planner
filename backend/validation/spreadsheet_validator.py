from collections import defaultdict

from backend.parsers.spreadsheet_parser import ParsedColumn
from backend.utils.text import name_key
from backend.validation.results import ValidationIssue, ValidationResult


def validate_columns(columns: list[ParsedColumn]) -> ValidationResult:
    """Check parsed spreadsheet columns and report problems in plain English."""
    result = ValidationResult()

    if not columns:
        result.errors.append(
            ValidationIssue(
                "The spreadsheet is empty. Put each dance name in the first row, "
                "with the dancers listed underneath it."
            )
        )
        return result

    _check_dance_names(columns, result)
    _check_empty_dances(columns, result)
    _check_duplicate_dancers_within_dances(columns, result)
    _check_name_spellings(columns, result)
    _check_first_name_matches(columns, result)
    return result


# ---------- errors (these block the show order) ----------


def _check_dance_names(columns: list[ParsedColumn], result: ValidationResult) -> None:
    columns_by_name = defaultdict(list)

    for column in columns:
        if not column.dance_name:
            result.errors.append(
                ValidationIssue(
                    f"Column {column.column_number} does not have a dance name in the first row.",
                    column.column_number,
                )
            )
        else:
            columns_by_name[name_key(column.dance_name)].append(column)

    for same_name in columns_by_name.values():
        if len(same_name) > 1:
            numbers = _join_words([str(column.column_number) for column in same_name])
            result.errors.append(
                ValidationIssue(
                    f"Columns {numbers} have the same dance name, '{same_name[0].dance_name}'. "
                    "Each dance needs a unique name.",
                    same_name[0].column_number,
                )
            )


def _check_empty_dances(columns: list[ParsedColumn], result: ValidationResult) -> None:
    for column in columns:
        if column.dance_name and not column.dancers:
            result.errors.append(
                ValidationIssue(
                    f"{_column_label(column)} has no dancers listed under it.",
                    column.column_number,
                )
            )


def _check_duplicate_dancers_within_dances(
    columns: list[ParsedColumn], result: ValidationResult
) -> None:
    for column in columns:
        first_spelling = {}
        already_reported = set()

        for dancer in column.dancers:
            key = name_key(dancer)
            if key in first_spelling and key not in already_reported:
                result.errors.append(
                    ValidationIssue(
                        f"{_column_label(column)} lists '{first_spelling[key]}' more than once.",
                        column.column_number,
                    )
                )
                already_reported.add(key)
            first_spelling.setdefault(key, dancer)


# ---------- warnings (shown, but don't block) ----------


def _check_name_spellings(columns: list[ParsedColumn], result: ValidationResult) -> None:
    """Warn when names differ only by capitalization or spacing."""
    spellings = defaultdict(list)  # comparison key -> distinct spellings, in order seen

    for column in columns:
        for dancer in column.dancers:
            key = name_key(dancer)
            if dancer not in spellings[key]:
                spellings[key].append(dancer)

    for variants in spellings.values():
        if len(variants) > 1:
            quoted = _join_words([f"'{name}'" for name in variants])
            result.warnings.append(
                ValidationIssue(
                    f"{quoted} will be treated as the same dancer. "
                    "If they are different people, give them different names in the spreadsheet."
                )
            )


def _check_first_name_matches(columns: list[ParsedColumn], result: ValidationResult) -> None:
    """Warn when a first name on its own matches the start of a full name."""
    names_by_key = {}  # comparison key -> first spelling seen
    for column in columns:
        for dancer in column.dancers:
            names_by_key.setdefault(name_key(dancer), dancer)

    for key, short_name in names_by_key.items():
        if " " in key:
            continue  # only look at single-word names like "Emma"

        longer_names = [
            full_name
            for other_key, full_name in names_by_key.items()
            if " " in other_key and other_key.split(" ")[0] == key
        ]
        if longer_names:
            options = _join_words([f"'{name}'" for name in longer_names], "or")
            result.warnings.append(
                ValidationIssue(
                    f"'{short_name}' might be the same person as {options}. "
                    "They are being treated as different dancers. "
                    "If they are the same person, use the same name everywhere."
                )
            )


# ---------- small helpers ----------


def _column_label(column: ParsedColumn) -> str:
    if column.dance_name:
        return f"Column {column.column_number} ('{column.dance_name}')"
    return f"Column {column.column_number}"


def _join_words(items: list[str], conjunction: str = "and") -> str:
    """['1'] -> '1', ['1', '5'] -> '1 and 5', ['1', '3', '5'] -> '1, 3 and 5'."""
    if len(items) <= 2:
        return f" {conjunction} ".join(items)
    return ", ".join(items[:-1]) + f" {conjunction} " + items[-1]