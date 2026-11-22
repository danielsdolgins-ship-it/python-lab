"""Flight Schedule Parser and Query Tool - command-line entry point.

Run from the project folder, for example:
    python flight_parser.py -i data/db.csv -a data/airports.txt
"""
import sys
import argparse
from datetime import datetime
import json
import logging
import os
from csv_loader import parse_files
from query import run_queries
from validator import load_airports

STUDENT_ID = "251RDC081"
FIRST_NAME = "Daniels"
LAST_NAME = "Dolgins"

class _ArgumentParserError(Exception):
    pass
class _StrictArgumentParser(argparse.ArgumentParser):

    def error(self, message: str) -> None:
        raise _ArgumentParserError(message)

def _build_parser() -> argparse.ArgumentParser:
    parser = _StrictArgumentParser(
        prog="flight_parser.py",
        description="Flight schedule parser and query tool.",
    )

    source_group = parser.add_mutually_exclusive_group()
    source_group.add_argument("-i", dest="input_file", help="Input CSV file path")
    source_group.add_argument("-d", dest="input_dir", help="Input folder path for CSV files")
    source_group.add_argument("-j", dest="json_db", help="Existing JSON database file path")

    parser.add_argument("-a", dest="airports_file", help="Airport list file path")
    parser.add_argument("-o", dest="output_db", default="db.json", help="Output JSON database path")
    parser.add_argument("-q", dest="query_file", help="Query JSON file path")
    parser.add_argument("-r", dest="response_dir", default=".", help="Response file output folder")
    return parser

def _collect_csv_paths(folder: str) -> list[str]:
    if not os.path.isdir(folder):
        raise FileNotFoundError(f"Directory not found: {folder}")
    csv_files = [
        os.path.join(folder, name)
        for name in sorted(os.listdir(folder))
        if name.lower().endswith(".csv") and os.path.isfile(os.path.join(folder, name))
    ]
    return csv_files




def main(argv: list[str] | None = None) -> int:
    """Run the whole program and return the exit code (0, 1 or 2).

    argv is the argument list without the program name.
    None means use sys.argv[1:] (argparse does this for you).
    Do not call sys.exit() inside main(); return the code instead.
    """
    parser = _build_parser()
    try:
        args = parser.parse_args(argv)
    except _ArgumentParserError as exc:
        sys.stderr.write(f"Argument error: {exc}\n")
        return 2

    has_source = any(x is not None for x in (args.input_file, args.input_dir, args.json_db))
    if not has_source:
        sys.stderr.write("Error: one of -i, -d, or -j is required.\n")
        return 1

    if args.json_db is not None and args.airports_file is not None:
        sys.stderr.write("Error: -a cannot be used with -j.\n")
        return 1

    if args.json_db is not None and args.output_db != "db.json":
        sys.stderr.write("Error: -o cannot be used with -j.\n")
        return 1

    if args.json_db is None and not args.airports_file:
        sys.stderr.write("Error: -a is required when using -i or -d.\n")
        return 1
    
    db: list[dict] = []
    # AI assisted
    logger = logging.getLogger("flight_parser")
    logger.setLevel(logging.INFO)
    logger.propagate = False
    handler: logging.FileHandler | None = None

    try:
        if args.json_db is not None:
            with open(args.json_db, "r", encoding="utf-8") as f:
                loaded = json.load(f)
            if not isinstance(loaded, list):
                sys.stderr.write("Error: JSON database must be a list.\n")
                return 1
            db = loaded
        else:
            airports = load_airports(args.airports_file)

            if args.input_file is not None:
                csv_paths = [args.input_file]
            else:
                csv_paths = _collect_csv_paths(args.input_dir)

            out_dir = os.path.dirname(args.output_db)
            log_path = os.path.join(out_dir, "errors.log") if out_dir else "errors.log"
            # AI assisted
            handler = logging.FileHandler(log_path, mode="w", encoding="utf-8")
            formatter = logging.Formatter(
                fmt="%(asctime)s %(levelname)s %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)

            records, errors = parse_files(csv_paths, airports)
            for err in errors:
                logger.error(err)

            if out_dir and not os.path.isdir(out_dir):
                os.makedirs(out_dir, exist_ok=True)

            with open(args.output_db, "w", encoding="utf-8") as f:
                json.dump(records, f, indent=2)

            db = records

        if args.query_file is not None:
            with open(args.query_file, "r", encoding="utf-8") as f:
                queries_data = json.load(f)

            responses = run_queries(db, queries_data)

            if not os.path.isdir(args.response_dir):
                os.makedirs(args.response_dir, exist_ok=True)

            stamp = datetime.now().strftime("%Y%m%d_%H%M")
            filename = f"response_{STUDENT_ID}_{FIRST_NAME}_{LAST_NAME}_{stamp}.json"
            response_path = os.path.join(args.response_dir, filename)

            with open(response_path, "w", encoding="utf-8") as f:
                json.dump(responses, f, indent=2)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        sys.stderr.write(f"Error: {exc}\n")
        return 1
        # AI assisted
    finally:
        if handler is not None:
            logger.removeHandler(handler)
            handler.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
