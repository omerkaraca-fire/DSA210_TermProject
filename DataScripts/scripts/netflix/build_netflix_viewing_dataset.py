#!/usr/bin/env python3
"""Build processed Netflix viewing-history outputs from the raw CSV export."""

from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_INPUT = REPO_ROOT / "data_local" / "raw" / "netflix" / "NetflixViewingHistory.csv"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "data_local" / "processed" / "netflix"

EXPECTED_COLUMNS = ["Title", "Date"]
OUTPUT_FIELDS = [
    "netflix_view_id",
    "source_file",
    "watch_date_raw",
    "watch_date_iso",
    "title",
    "title_missing",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build processed Netflix viewing-history CSV and JSONL outputs."
    )
    parser.add_argument(
        "--input-csv",
        default=str(DEFAULT_INPUT),
        help="Path to the raw Netflix viewing-history CSV export.",
    )
    parser.add_argument(
        "--output-dir",
        default=str(DEFAULT_OUTPUT_DIR),
        help="Directory where processed Netflix outputs will be written.",
    )
    return parser.parse_args()


def safe_text(value: str | None) -> str:
    return (value or "").strip()


def repo_relative_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def parse_watch_date(raw_value: str) -> str:
    text = safe_text(raw_value)
    if not text:
        return ""

    # Netflix exports dates in a short month/day/year format.
    for fmt in ("%m/%d/%y", "%m/%d/%Y"):
        try:
            return datetime.strptime(text, fmt).date().isoformat()
        except ValueError:
            continue
    return ""


def read_raw_rows(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        fieldnames = [safe_text(name) for name in (reader.fieldnames or [])]

        if fieldnames != EXPECTED_COLUMNS:
            raise ValueError(
                f"Expected raw Netflix columns {EXPECTED_COLUMNS!r}, found {fieldnames!r}."
            )

        rows: list[dict[str, str]] = []
        source_file = repo_relative_path(path)

        for index, raw_row in enumerate(reader, start=1):
            title = safe_text(raw_row.get("Title"))
            watch_date_raw = safe_text(raw_row.get("Date"))
            watch_date_iso = parse_watch_date(watch_date_raw)

            # Keep the raw title untouched for now instead of guessing show/episode parts.
            rows.append(
                {
                    "netflix_view_id": f"netflix_view_{index:06d}",
                    "source_file": source_file,
                    "watch_date_raw": watch_date_raw,
                    "watch_date_iso": watch_date_iso,
                    "title": title,
                    "title_missing": "true" if not title else "false",
                }
            )

    return fieldnames, rows


def write_csv_rows(rows: list[dict[str, str]], fieldnames: list[str], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_jsonl_rows(rows: list[dict[str, str]], fieldnames: list[str], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        for row in rows:
            ordered_row = {field: row.get(field, "") for field in fieldnames}
            handle.write(json.dumps(ordered_row, ensure_ascii=False) + "\n")


def date_range(rows: list[dict[str, str]]) -> dict[str, str]:
    valid_dates = sorted(
        row["watch_date_iso"] for row in rows if safe_text(row.get("watch_date_iso"))
    )
    if not valid_dates:
        return {"min": "", "max": ""}
    return {"min": valid_dates[0], "max": valid_dates[-1]}


def build_outputs(*, input_csv: Path, output_dir: Path) -> dict[str, Any]:
    if not input_csv.is_file():
        raise FileNotFoundError(f"Raw Netflix viewing-history CSV not found: {input_csv}")

    raw_columns, rows = read_raw_rows(input_csv)

    csv_output = output_dir / "netflix_viewing_history_processed.csv"
    jsonl_output = output_dir / "netflix_viewing_history_processed.jsonl"
    summary_output = output_dir / "build_summary.json"

    write_csv_rows(rows, OUTPUT_FIELDS, csv_output)
    write_jsonl_rows(rows, OUTPUT_FIELDS, jsonl_output)

    summary_payload = {
        "dataset": "netflix_viewing_history_processed",
        "input_file": repo_relative_path(input_csv),
        "raw_columns": raw_columns,
        "row_count": len(rows),
        "invalid_date_count": sum(1 for row in rows if not row["watch_date_iso"]),
        "title_missing_count": sum(1 for row in rows if row["title_missing"] == "true"),
        "date_range": date_range(rows),
        "files": {
            "csv": csv_output.name,
            "jsonl": jsonl_output.name,
            "summary": summary_output.name,
        },
        "schema": OUTPUT_FIELDS,
    }

    summary_output.parent.mkdir(parents=True, exist_ok=True)
    summary_output.write_text(
        json.dumps(summary_payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    return {
        "input_csv": str(input_csv),
        "output_dir": str(output_dir),
        "row_count": summary_payload["row_count"],
        "invalid_date_count": summary_payload["invalid_date_count"],
        "title_missing_count": summary_payload["title_missing_count"],
        "date_range": summary_payload["date_range"],
        "outputs": {
            "csv": str(csv_output),
            "jsonl": str(jsonl_output),
            "summary": str(summary_output),
        },
    }


def main() -> None:
    args = parse_args()
    summary = build_outputs(
        input_csv=Path(args.input_csv),
        output_dir=Path(args.output_dir),
    )
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
