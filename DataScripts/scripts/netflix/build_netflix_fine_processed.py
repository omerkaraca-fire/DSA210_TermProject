#!/usr/bin/env python3
"""Build local reusable Netflix fine_processed exports from the processed table."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_INPUT = REPO_ROOT / "data_local" / "processed" / "netflix" / "netflix_viewing_history_processed.csv"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "data_local" / "fine_processed"

COMMON_FIELDS = [
    "fine_platform",
    "fine_table",
    "fine_record_id",
    "fine_account",
    "fine_source_file",
    "fine_time_start",
    "fine_time_end",
    "fine_time_granularity",
    "fine_date",
]
OUTPUT_FIELDS = COMMON_FIELDS + ["title", "title_missing"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build local fine_processed Netflix CSV and JSONL exports."
    )
    parser.add_argument(
        "--input-csv",
        default=str(DEFAULT_INPUT),
        help="Path to the processed Netflix viewing-history CSV.",
    )
    parser.add_argument(
        "--output-dir",
        default=str(DEFAULT_OUTPUT_DIR),
        help="Directory where local fine_processed outputs will be written.",
    )
    return parser.parse_args()


def safe_text(value: str | None) -> str:
    return (value or "").strip()


def normalize_source_file(value: str) -> str:
    text = safe_text(value)
    if not text:
        return ""

    path = Path(text)
    if path.is_absolute():
        try:
            return str(path.relative_to(REPO_ROOT))
        except ValueError:
            return text
    return text


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def build_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    fine_rows: list[dict[str, str]] = []

    for index, row in enumerate(rows, start=1):
        watch_date_iso = safe_text(row.get("watch_date_iso"))
        record_id = safe_text(row.get("netflix_view_id")) or f"netflix_view_{index:06d}"

        # Netflix only gives a viewing date, so the fine layer stays date-granular.
        fine_rows.append(
            {
                "fine_platform": "netflix",
                "fine_table": "netflix_viewing_history_local",
                "fine_record_id": record_id,
                "fine_account": "",
                "fine_source_file": normalize_source_file(row.get("source_file") or ""),
                "fine_time_start": watch_date_iso,
                "fine_time_end": watch_date_iso,
                "fine_time_granularity": "date" if watch_date_iso else "none",
                "fine_date": watch_date_iso,
                "title": safe_text(row.get("title")),
                "title_missing": "true"
                if safe_text(row.get("title_missing")).lower() == "true"
                else "false",
            }
        )

    return fine_rows


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


def build_outputs(*, input_csv: Path, output_dir: Path) -> dict[str, Any]:
    if not input_csv.is_file():
        raise FileNotFoundError(f"Processed Netflix input not found: {input_csv}")

    fine_rows = build_rows(read_csv_rows(input_csv))

    csv_output = output_dir / "fine_netflix_viewing_history_local.csv"
    jsonl_output = output_dir / "fine_netflix_viewing_history_local.jsonl"

    write_csv_rows(fine_rows, OUTPUT_FIELDS, csv_output)
    write_jsonl_rows(fine_rows, OUTPUT_FIELDS, jsonl_output)

    return {
        "input_csv": str(input_csv),
        "output_dir": str(output_dir),
        "row_count": len(fine_rows),
        "invalid_date_count": sum(1 for row in fine_rows if not row["fine_date"]),
        "title_missing_count": sum(1 for row in fine_rows if row["title_missing"] == "true"),
        "outputs": {
            "csv": str(csv_output),
            "jsonl": str(jsonl_output),
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
