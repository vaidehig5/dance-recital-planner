from pathlib import Path

from backend.parsers.spreadsheet_parser import ParsedColumn, parse_spreadsheet
from backend.validation.spreadsheet_validator import validate_columns

SAMPLE_DIR = Path(__file__).resolve().parent.parent / "sample_data"


def col(number, name, *dancers):
    return ParsedColumn(number, name, list(dancers))


def messages(issues):
    return [issue.message for issue in issues]


def test_clean_sample_file_has_no_errors_or_warnings():
    content = (SAMPLE_DIR / "sample_recital.csv").read_bytes()
    result = validate_columns(parse_spreadsheet("sample_recital.csv", content))

    assert result.is_valid
    assert result.errors == []
    assert result.warnings == []


def test_empty_spreadsheet_is_an_error():
    result = validate_columns([])

    assert not result.is_valid
    assert len(result.errors) == 1
    assert "empty" in result.errors[0].message


def test_missing_dance_name_is_reported_with_column_number():
    result = validate_columns([col(1, "Ballet", "Bob"), col(4, "", "Alice")])

    assert messages(result.errors) == [
        "Column 4 does not have a dance name in the first row."
    ]
    assert result.errors[0].column_number == 4


def test_duplicate_dance_names_are_reported_ignoring_capitalization():
    result = validate_columns([col(1, "Ballet", "Alice"), col(3, "ballet", "Bob")])

    assert messages(result.errors) == [
        "Columns 1 and 3 have the same dance name, 'Ballet'. Each dance needs a unique name."
    ]


def test_dance_with_no_dancers_is_an_error():
    result = validate_columns([col(1, "Ballet", "Alice"), col(2, "Jazz")])

    assert messages(result.errors) == ["Column 2 ('Jazz') has no dancers listed under it."]


def test_duplicate_dancer_within_one_dance_is_an_error():
    result = validate_columns([col(2, "Jazz", "Alice", "Maya", "alice")])

    assert messages(result.errors) == ["Column 2 ('Jazz') lists 'Alice' more than once."]


def test_same_dancer_in_different_dances_is_fine():
    result = validate_columns([col(1, "Ballet", "Alice"), col(2, "Jazz", "Alice")])

    assert result.is_valid
    assert result.warnings == []


def test_spelling_variants_produce_a_warning_not_an_error():
    result = validate_columns([col(1, "Ballet", "Alice"), col(2, "Jazz", "alice")])

    assert result.is_valid
    assert messages(result.warnings) == [
        "'Alice' and 'alice' will be treated as the same dancer. "
        "If they are different people, give them different names in the spreadsheet."
    ]


def test_first_name_matching_a_full_name_produces_a_warning():
    result = validate_columns([col(1, "Ballet", "Emma"), col(2, "Jazz", "Emma Smith")])

    assert result.is_valid
    assert messages(result.warnings) == [
        "'Emma' might be the same person as 'Emma Smith'. "
        "They are being treated as different dancers. "
        "If they are the same person, use the same name everywhere."
    ]


def test_two_full_names_sharing_a_first_name_do_not_warn():
    result = validate_columns(
        [col(1, "Ballet", "Emma Smith"), col(2, "Jazz", "Emma Jones")]
    )

    assert result.is_valid
    assert result.warnings == []


def test_messy_sample_reports_every_problem():
    content = (SAMPLE_DIR / "messy_recital.csv").read_bytes()
    result = validate_columns(parse_spreadsheet("messy_recital.csv", content))

    assert not result.is_valid
    assert messages(result.errors) == [
        "Column 3 does not have a dance name in the first row.",
        "Column 1 ('Ballet by Sarah') lists 'emma' more than once.",
        "Column 4 ('Tap by Maria') lists 'Priya' more than once.",
    ]
    assert len(result.warnings) == 2