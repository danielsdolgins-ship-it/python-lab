"""Running queries against the flight database."""
import math

def _is_valid_datetime_str(value: str) -> bool:
    if not isinstance(value, str):
        return False
    if len(value) != 16:
        return False
    if value[4] != "-" or value[7] != "-" or value[10] != " " or value[13] != ":":
        return False
    return True

def _is_valid_number(value: object) -> bool:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return False
    return math.isfinite(value)

def run_query(db: list[dict], query: dict) -> dict:
    """Return one response entry for one query object.

    Valid query:   {"query": query, "matches": [...]}
    Invalid query: {"query": query, "error": "INVALID_QUERY", "matches": []}
    """
    allowed_keys = {
        "flight_id",
        "origin",
        "destination",
        "departure_datetime",
        "arrival_datetime",
        "price",
        "min_price",
        "sort_by",
        "order",
        "limit",
    }
    # AI assisted
    sortable_fields = {
        "flight_id",
        "origin",
        "destination",
        "departure_datetime",
        "arrival_datetime",
        "price",
    }



    if not isinstance(query, dict):
        return {"query": query, "error": "INVALID_QUERY", "matches": []}

    for key in query:
        if not isinstance(key, str) or key not in allowed_keys:
            return {"query": query, "error": "INVALID_QUERY", "matches": []}

    if "order" in query and "sort_by" not in query:
        return {"query": query, "error": "INVALID_QUERY", "matches": []}

    for field in ("flight_id", "origin", "destination"):
        if field in query and not isinstance(query[field], str):
            return {"query": query, "error": "INVALID_QUERY", "matches": []}

    for dt_field in ("departure_datetime", "arrival_datetime"):
        if dt_field in query and not _is_valid_datetime_str(query[dt_field]):
            return {"query": query, "error": "INVALID_QUERY", "matches": []}

    for price_field in ("price", "min_price"):
        if price_field in query and not _is_valid_number(query[price_field]):
            return {"query": query, "error": "INVALID_QUERY", "matches": []}

    if "sort_by" in query:
        sort_by = query["sort_by"]
        if not isinstance(sort_by, str) or sort_by not in sortable_fields:
            return {"query": query, "error": "INVALID_QUERY", "matches": []}

    if "order" in query:
        order = query["order"]
        if not isinstance(order, str) or order not in ("asc", "desc"):
            return {"query": query, "error": "INVALID_QUERY", "matches": []}

    if "limit" in query:
        limit = query["limit"]
        if isinstance(limit, bool) or not isinstance(limit, int) or limit < 0:
            return {"query": query, "error": "INVALID_QUERY", "matches": []}

    matches = []
    for row in db:
        if "flight_id" in query and row.get("flight_id") != query["flight_id"]:
            continue
        if "origin" in query and row.get("origin") != query["origin"]:
            continue
        if "destination" in query and row.get("destination") != query["destination"]:
            continue
        if "departure_datetime" in query and row.get("departure_datetime", "") < query["departure_datetime"]:
            continue
        if "arrival_datetime" in query and row.get("arrival_datetime", "") > query["arrival_datetime"]:
            continue
        if "price" in query and row.get("price", float("inf")) > query["price"]:
            continue
        if "min_price" in query and row.get("price", float("-inf")) < query["min_price"]:
            continue
        matches.append(row)

    if "sort_by" in query:
        sort_key = query["sort_by"]
        reverse = query.get("order", "asc") == "desc"
        matches = sorted(matches, key=lambda item: item[sort_key], reverse=reverse)

    if "limit" in query:
        matches = matches[: query["limit"]]

    # AI assisted
    return {"query": query, "matches": matches}

# AI assisted
def run_queries(db: list[dict], queries: dict | list) -> list[dict]:
    """Accept one query object or a list of them; always return a list."""
    if isinstance(queries, dict):
        query_list = [queries]
    elif isinstance(queries, list):
        query_list = queries
    else:
        return [run_query(db, queries)]

    return [run_query(db, q) for q in query_list]
