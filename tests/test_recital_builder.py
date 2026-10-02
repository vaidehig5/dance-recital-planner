from dataclasses import asdict
from pathlib import Path

from backend.models.dance import Dance
from backend.parsers.spreadsheet_parser import ParsedColumn, parse_spreadsheet
from backend.services.recital_builder import build_recital

SAMPLE_DIR = Path(__file__).resolve().parent.parent / "sample_data"


def col(number, name, *dancers):
    return ParsedColumn(number, name, list(dancers))


def dancer_named(recital, name):
    return next(dancer for dancer in recital.dancers if dancer.name == name)


def test_one_dance_per_column_in_spreadsheet_order():
    recital = build_recital([col(1, "Ballet", "Alice"), col(3, "Jazz", "Bob")])

    assert [dance.id for dance in recital.dances] == [1, 2]
    assert [dance.name for dance in recital.dances] == ["Ballet", "Jazz"]


def test_shared_dancer_is_one_person_linked_to_both_dances():
    recital = build_recital(
        [col(1, "Ballet", "Alice", "Emma"), col(2, "Jazz", "Maya", "Alice")]
    )

    assert [dancer.name for dancer in recital.dancers] == ["Alice", "Emma", "Maya"]
    assert recital.dances[0].dancer_ids == [1, 2]
    assert recital.dances[1].dancer_ids == [3, 1]
    assert dancer_named(recital, "Alice").dance_ids == [1, 2]


def test_spelling_variants_become_one_dancer_using_the_first_spelling():
    recital = build_recital([col(1, "Ballet", "Alice"), col(2, "Jazz", "alice")])

    assert len(recital.dancers) == 1
    assert recital.dancers[0].name == "Alice"
    assert recital.dancers[0].dance_ids == [1, 2]


def test_first_name_and_full_name_stay_separate_dancers():
    recital = build_recital([col(1, "Ballet", "Emma"), col(2, "Jazz", "Emma Smith")])

    assert [dancer.name for dancer in recital.dancers] == ["Emma", "Emma Smith"]


def test_dancer_listed_twice_in_one_dance_is_only_counted_once():
    recital = build_recital([col(1, "Ballet", "Alice", "alice")])

    assert len(recital.dancers) == 1
    assert recital.dances[0].dancer_ids == [1]
    assert recital.dancers[0].dance_ids == [1]


def test_duration_and_style_start_empty():
    recital = build_recital([col(1, "Ballet", "Alice")])

    assert recital.dances[0].duration_seconds is None
    assert recital.dances[0].style is None


def test_sample_recital_file_builds_the_expected_model():
    content = (SAMPLE_DIR / "sample_recital.csv").read_bytes()
    recital = build_recital(parse_spreadsheet("sample_recital.csv", content))

    assert len(recital.dances) == 4
    assert [dancer.name for dancer in recital.dancers] == [
        "Alice",
        "Emma",
        "Sarah",
        "Jessica",
        "Maya",
    ]
    assert dancer_named(recital, "Alice").dance_ids == [1, 2, 3, 4]
    assert dancer_named(recital, "Emma").dance_ids == [1, 3, 4]


def test_each_dance_gets_its_own_dancer_list():
    first = Dance(id=1, name="Ballet")
    second = Dance(id=2, name="Jazz")

    first.dancer_ids.append(7)

    assert second.dancer_ids == []


def test_recital_converts_to_plain_dictionaries_for_json():
    data = asdict(build_recital([col(1, "Ballet", "Alice")]))

    assert data["dances"][0] == {
        "id": 1,
        "name": "Ballet",
        "dancer_ids": [1],
        "duration_seconds": None,
        "style": None,
    }
    assert data["dancers"][0] == {"id": 1, "name": "Alice", "dance_ids": [1]}