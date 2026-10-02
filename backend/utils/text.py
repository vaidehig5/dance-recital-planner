def clean_text(value) -> str:
    """Trim a cell value and collapse any run of whitespace into one space.

    None becomes an empty string, and non-text values (like numbers from
    Excel) are converted to text first.
    """
    if value is None:
        return ""
    return " ".join(str(value).split())


def name_key(name: str) -> str:
    """A comparison key so ' Alice ', 'alice' and 'Alice' count as the same name.

    Not used by the parser itself. Later phases use it to decide whether
    two spellings refer to the same dancer.
    """
    return clean_text(name).casefold()