#!/usr/bin/env python3
"""Build local reusable Prime Video fine_processed exports from the processed table."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_INPUT = REPO_ROOT / "data_local" / "processed" / "prime_video" / "prime_video_watch_history.csv"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "data_local" / "fine_processed"
DEFAULT_SOURCE_FILE = "data_local/raw/prime_video/raw.txt"

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
OUTPUT_FIELDS = COMMON_FIELDS + [
    "record_type",
    "title",
    "series_title",
    "season_number",
    "episode_number",
    "episode_title",
    "movie_title",
    "title_missing",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build local fine_processed Prime Video CSV and JSONL exports."
    )
    parser.add_argument(
        "--input-csv",
        default=str(DEFAULT_INPUT),
        help="Path to the processed Prime Video watch-history CSV.",
    )
    parser.add_argument(
        "--output-dir",
        default=str(DEFAULT_OUTPUT_DIR),
        help="Directory where local fine_processed outputs will be written.",
    )
    parser.add_argument(
        "--source-file",
        default=DEFAULT_SOURCE_FILE,
        help="Source file reference stored in fine_source_file.",
    )
    return parser.parse_args()


def safe_text(value: str | None) -> str:
    return (value or "").strip()


def load_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


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


def build_rows(rows: list[dict[str, str]], source_file: str) -> list[dict[str, str]]:
    fine_rows: list[dict[str, str]] = []

    for index, row in enumerate(rows, start=1):
        watch_date = safe_text(row.get("watch_date"))
        record_id = safe_text(row.get("record_id")) or f"prime_video_{index:06d}"
        fine_rows.append(
            {
                "fine_platform": "prime_video",
                "fine_table": "prime_video_watch_history_local",
                "fine_record_id": record_id,
                "fine_account": "",
                "fine_source_file": source_file,
                "fine_time_start": watch_date,
                "fine_time_end": watch_date,
                "fine_time_granularity": "date" if watch_date else "none",
                "fine_date": watch_date,
                "record_type": safe_text(row.get("record_type")),
                "title": safe_text(row.get("title")),
                "series_title": safe_text(row.get("series_title")),
                "season_number": safe_text(row.get("season_number")),
                "episode_number": safe_text(row.get("episode_number")),
                "episode_title": safe_text(row.get("episode_title")),
                "movie_title": safe_text(row.get("movie_title")),
                "title_missing": "true"
                if safe_text(row.get("title_missing")).lower() in {"true", "1"}
                else "false",
            }
        )

    return fine_rows


def build_outputs(*, input_csv: Path, output_dir: Path, source_file: str = DEFAULT_SOURCE_FILE) -> dict[str, Any]:
    if not input_csv.is_file():
        raise FileNotFoundError(f"Processed Prime Video input not found: {input_csv}")

    fine_rows = build_rows(load_rows(input_csv), source_file)

    csv_output = output_dir / "fine_prime_video_watch_history_local.csv"
    jsonl_output = output_dir / "fine_prime_video_watch_history_local.jsonl"

    write_csv_rows(fine_rows, OUTPUT_FIELDS, csv_output)
    write_jsonl_rows(fine_rows, OUTPUT_FIELDS, jsonl_output)

    return {
        "input_csv": str(input_csv),
        "output_dir": str(output_dir),
        "row_count": len(fine_rows),
        "date_range": {
            "min": min((row["fine_date"] for row in fine_rows if row["fine_date"]), default=""),
            "max": max((row["fine_date"] for row in fine_rows if row["fine_date"]), default=""),
        },
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
        source_file=args.source_file,
    )
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
