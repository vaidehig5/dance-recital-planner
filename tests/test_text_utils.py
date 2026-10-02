from backend.utils.text import clean_text, name_key


def test_clean_text_handles_none():
    assert clean_text(None) == ""


def test_clean_text_trims_ends():
    assert clean_text("  Alice  ") == "Alice"


def test_clean_text_collapses_inner_spaces():
    assert clean_text("Mary    Jane") == "Mary Jane"


def test_clean_text_handles_non_breaking_spaces():
    assert clean_text("\u00a0Alice\u00a0") == "Alice"


def test_name_key_ignores_case_and_spacing():
    assert name_key(" Alice ") == name_key("alice") == name_key("Alice")