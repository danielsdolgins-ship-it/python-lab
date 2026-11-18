"""Reading CSV files into flight records and error messages."""


import csv
import os
from validator import validate_row, to_record

def parse_files(paths: list[str], airports: set[str]) -> tuple[list[dict], list[str]]:
    """Process the CSV files in the order given.

    Return (records, errors):
      records - valid flight records, in input order
      errors  - one message per invalid row, in input order, formatted as
                "<file name>:<line number>: <ERROR_CODE> | <free text>"
                (base file name only, no timestamp or level, no newline)

    Also performs the DUPLICATE_FLIGHT check across all the files.
    Does not write any files and does not log anything itself.
    """
    valid_records = []
    error_messages = []
    seen_flights = set()

    for path in paths:
        filename = os.path.basename(path)
        with open(path, "r", encoding="utf-8", newline="") as f:
            lines = f.readlines()

        for line_idx, line in enumerate(lines, start=1):
            stripped_line = line.strip()
            
            if not stripped_line:
                continue
            if stripped_line.startswith("#"):
                continue

            if line_idx == 1 and "flight_id" in stripped_line:
                continue

            reader = csv.reader([line])
            fields = next(reader, None)
            if not fields:
                continue

            err_code = validate_row(fields, airports)

            if err_code is None:
                cleaned_fields = [f.strip() for f in fields]
                flight_key = (cleaned_fields[0], cleaned_fields[3])
                
                if flight_key in seen_flights:
                    err_code = "DUPLICATE_FLIGHT"
                else:
                    seen_flights.add(flight_key)

            if err_code is not None:
                msg = f"{filename}:{line_idx}: {err_code} | {stripped_line}"
                error_messages.append(msg)
            else:
                valid_records.append(to_record(fields))

    return valid_records, error_messages