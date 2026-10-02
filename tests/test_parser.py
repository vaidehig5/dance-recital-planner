from io import BytesIO
from pathlib import Path

import pytest
from openpyxl import Workbook

from backend.parsers.errors import SpreadsheetError
from backend.parsers.spreadsheet_parser import parse_spreadsheet

SAMPLE_DIR = Path(__file__).resolve().parent.parent / "sample_data"


def csv_bytes(text: str) -> bytes:
    return text.encode("utf-8")


def xlsx_bytes(rows) -> bytes:
    workbook = Workbook()
    sheet = workbook.active
    for row in rows:
        sheet.append(row)
    buffer = BytesIO()
    workbook.save(buffer)
    return buffer.getvalue()


def test_first_row_is_the_dance_name_not_a_dancer():
    columns = parse_spreadsheet(
        "show.csv", csv_bytes("Ballet by Sarah,Jazz by Emily\nAlice,Maya\nEmma,Alice\n")
    )

    assert [c.dance_name for c in columns] == ["Ballet by Sarah", "Jazz by Emily"]
    assert columns[0].dancers == ["Alice", "Emma"]
    assert columns[1].dancers == ["Maya", "Alice"]


def test_blank_cells_are_ignored():
    columns = parse_spreadsheet("show.csv", csv_bytes("Ballet,Jazz\nAlice,Maya\n,Alice\nEmma,\n"))

    assert columns[0].dancers == ["Alice", "Emma"]
    assert columns[1].dancers == ["Maya", "Alice"]


def test_whitespace_is_trimmed_and_collapsed():
    columns = parse_spreadsheet("show.csv", csv_bytes(" Ballet by  Sarah ,Jazz\n  Alice  ,Maya\n"))

    assert columns[0].dance_name == "Ballet by Sarah"
    assert columns[0].dancers == ["Alice"]


def test_parser_does_not_change_capitalization():
    columns = parse_spreadsheet("show.csv", csv_bytes("Ballet\nalice\nAlice\n"))

    assert columns[0].dancers == ["alice", "Alice"]


def test_empty_column_is_dropped_but_column_numbers_stay_original():
    columns = parse_spreadsheet("show.csv", csv_bytes("Ballet,,Tap\nAlice,,Bob\n"))

    assert [c.column_number for c in columns] == [1, 3]
    assert [c.dance_name for c in columns] == ["Ballet", "Tap"]


def test_column_with_dancers_but_no_dance_name_is_kept():
    columns = parse_spreadsheet("show.csv", csv_bytes("Ballet,\nAlice,Bob\n"))

    assert columns[1].column_number == 2
    assert columns[1].dance_name == ""
    assert columns[1].dancers == ["Bob"]


def test_column_with_dance_name_but_no_dancers_is_kept():
    columns = parse_spreadsheet("show.csv", csv_bytes("Ballet,Jazz\nAlice,\n"))

    assert columns[1].dance_name == "Jazz"
    assert columns[1].dancers == []


def test_duplicate_dancers_in_one_dance_are_kept_for_validation():
    columns = parse_spreadsheet("show.csv", csv_bytes("Ballet\nAlice\nAlice\n"))

    assert columns[0].dancers == ["Alice", "Alice"]


def test_xlsx_file_is_parsed_like_csv():
    rows = [
        ["Ballet by Sarah", "Jazz by Emily"],
        ["Alice", "Maya"],
        ["Emma", None],
        [None, "Alice"],
    ]
    columns = parse_spreadsheet("show.xlsx", xlsx_bytes(rows))

    assert [c.dance_name for c in columns] == ["Ballet by Sarah", "Jazz by Emily"]
    assert columns[0].dancers == ["Alice", "Emma"]
    assert columns[1].dancers == ["Maya", "Alice"]


def test_unsupported_file_type_gives_friendly_error():
    with pytest.raises(SpreadsheetError, match="supported"):
        parse_spreadsheet("notes.txt", b"hello")


def test_damaged_xlsx_gives_friendly_error():
    with pytest.raises(SpreadsheetError, match="Excel"):
        parse_spreadsheet("bad.xlsx", b"this is not a real excel file")


def test_empty_csv_returns_no_columns():
    assert parse_spreadsheet("empty.csv", b"") == []


def test_csv_with_excel_bom_marker_is_read_correctly():
    columns = parse_spreadsheet("show.csv", csv_bytes("\ufeffBallet\nAlice\n"))

    assert columns[0].dance_name == "Ballet"


def test_sample_recital_csv_is_parsed_correctly():
    content = (SAMPLE_DIR / "sample_recital.csv").read_bytes()
    columns = parse_spreadsheet("sample_recital.csv", content)

    assert [c.dance_name for c in columns] == [
        "Ballet by Sarah",
        "Jazz by Emily",
        "Hip Hop by Rachel",
        "Contemporary by Sarah",
    ]
    assert columns[0].dancers == ["Alice", "Emma", "Sarah", "Jessica"]
    assert columns[1].dancers == ["Maya", "Alice", "Jessica"]


def test_messy_sample_keeps_problems_visible_for_validation():
    content = (SAMPLE_DIR / "messy_recital.csv").read_bytes()
    columns = parse_spreadsheet("messy_recital.csv", content)

    assert [c.column_number for c in columns] == [1, 2, 3, 4]
    assert columns[0].dance_name == "Ballet by Sarah"
    assert columns[0].dancers == ["Alice", "emma", "Emma"]
    assert columns[2].dance_name == ""
    assert columns[2].dancers == ["Alice"]
    assert columns[3].dancers == ["Priya", "Priya"]