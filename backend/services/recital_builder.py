from backend.models.dance import Dance
from backend.models.dancer import Dancer
from backend.models.recital import Recital
from backend.parsers.spreadsheet_parser import ParsedColumn
from backend.utils.text import name_key


def build_recital(columns: list[ParsedColumn]) -> Recital:
    """Turn parsed spreadsheet columns into Dance and Dancer objects.

    Dancers are matched with name_key(), so 'Alice', ' alice ' and 'ALICE'
    become a single Dancer. Expects columns that already passed validation.
    """
    recital = Recital()
    dancers_by_key: dict[str, Dancer] = {}

    for dance_number, column in enumerate(columns, start=1):
        dance = Dance(id=dance_number, name=column.dance_name)

        for dancer_name in column.dancers:
            key = name_key(dancer_name)
            dancer = dancers_by_key.get(key)

            if dancer is None:
                dancer = Dancer(id=len(recital.dancers) + 1, name=dancer_name)
                dancers_by_key[key] = dancer
                recital.dancers.append(dancer)

            if dancer.id in dance.dancer_ids:
                continue  # safety net: validation already rejects duplicates in one dance

            dance.dancer_ids.append(dancer.id)
            dancer.dance_ids.append(dance.id)

        recital.dances.append(dance)

    return recital