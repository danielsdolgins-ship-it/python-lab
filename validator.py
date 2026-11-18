"""Row validation: airport list loading, single-row checks, record building."""
from datetime import datetime


def load_airports(path: str) -> set[str]:
    """Read an airport list file and return the set of codes.

    One code per line. Strip whitespace; skip blank lines and lines
    starting with '#'.
    """
    airports = set()
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                airports.add(line)
    return airports

def validate_row(fields: list[str], airports: set[str]) -> str | None:
    """Check one CSV row (fields as returned by csv.reader, not yet stripped).

    Return None if the row is valid, otherwise the error code of the
    FIRST failing check (checks 1-11 in the specification, in order).
    Does not check for duplicates.
    """
    if len(fields) != 6:
        return "WRONG_FIELD_COUNT"

    stripped = [f.strip() for f in fields]
    flight_id, origin, destination, dep_str, arr_str, price_str = stripped

    if not all(stripped):
        return "MISSING_FIELD"

    if not (2 <= len(flight_id) <= 8 and flight_id.isalnum() and flight_id.isascii()):
        return "INVALID_FLIGHT_ID"

    if not (len(origin) == 3 and origin.isupper() and origin.isascii() and origin in airports):
        return "INVALID_ORIGIN"

    if not (len(destination) == 3 and destination.isupper() and destination.isascii() and destination in airports):
        return "INVALID_DESTINATION"

    if origin == destination:
        return "SAME_ORIGIN_DESTINATION"

    def is_valid_datetime(dt_str: str) -> bool:
        try:
            if len(dt_str) != 16 or dt_str[4] != '-' or dt_str[7] != '-' or dt_str[10] != ' ' or dt_str[13] != ':':
                return False
            datetime.strptime(dt_str, "%Y-%m-%d %H:%M")
            return True
        except ValueError:
            return False

    if not is_valid_datetime(dep_str):
        return "INVALID_DEPARTURE"

    if not is_valid_datetime(arr_str):
        return "INVALID_ARRIVAL"

    dep_dt = datetime.strptime(dep_str, "%Y-%m-%d %H:%M")
    arr_dt = datetime.strptime(arr_str, "%Y-%m-%d %H:%M")

    if arr_dt <= dep_dt:
        return "ARRIVAL_NOT_AFTER_DEPARTURE"

    try:
        price = float(price_str)
        if price != price or price == float('inf') or price == float('-inf'):
            return "INVALID_PRICE"
    except ValueError:
        return "INVALID_PRICE"

    if price <= 0:
        return "NON_POSITIVE_PRICE"

    return None

def to_record(fields: list[str]) -> dict:
    """Turn a valid row into a flight record dictionary.

    Keys: flight_id, origin, destination, departure_datetime,
    arrival_datetime (stripped strings) and price (float).
    """
    stripped = [f.strip() for f in fields]
    return {
        "flight_id": stripped[0],
        "origin": stripped[1],
        "destination": stripped[2],
        "departure_datetime": stripped[3],
        "arrival_datetime": stripped[4],
        "price": float(stripped[5])
    }