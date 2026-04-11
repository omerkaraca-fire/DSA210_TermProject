#!/usr/bin/env python3
"""Build local reusable Spotify fine_processed exports from the processed table."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_INPUT = (
    REPO_ROOT / "data_local" / "processed" / "spotify" / "spotify_streaming_history_processed.csv"
)
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
OUTPUT_FIELDS = COMMON_FIELDS + [
    "source_kind",
    "playback_platform",
    "track_name",
    "artist_name",
    "album_name",
    "spotify_track_uri",
    "ms_played",
    "minutes_played",
    "hours_played",
    "shuffle",
    "skipped",
    "offline",
    "incognito_mode",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build local fine_processed Spotify CSV and JSONL exports."
    )
    parser.add_argument(
        "--input-csv",
        default=str(DEFAULT_INPUT),
        help="Path to the processed Spotify streaming CSV.",
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


def build_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    fine_rows: list[dict[str, str]] = []

    for index, row in enumerate(rows, start=1):
        record_id = safe_text(row.get("spotify_stream_id")) or f"spotify_stream_{index:06d}"
        end_time = safe_text(row.get("timestamp_end_utc"))
        start_time = safe_text(row.get("timestamp_start_utc")) or end_time

        fine_rows.append(
            {
                "fine_platform": "spotify",
                "fine_table": "spotify_streaming_local",
                "fine_record_id": record_id,
                "fine_account": safe_text(row.get("account_label")),
                "fine_source_file": normalize_source_file(row.get("source_file") or ""),
                "fine_time_start": start_time,
                "fine_time_end": end_time,
                "fine_time_granularity": "timestamp" if end_time else "none",
                "fine_date": safe_text(row.get("date_utc")),
                "source_kind": safe_text(row.get("source_kind")),
                "playback_platform": safe_text(row.get("playback_platform")),
                "track_name": safe_text(row.get("track_name")),
                "artist_name": safe_text(row.get("artist_name")),
                "album_name": safe_text(row.get("album_name")),
                "spotify_track_uri": safe_text(row.get("spotify_track_uri")),
                "ms_played": safe_text(row.get("ms_played")),
                "minutes_played": safe_text(row.get("minutes_played")),
                "hours_played": safe_text(row.get("hours_played")),
                "shuffle": safe_text(row.get("shuffle")),
                "skipped": safe_text(row.get("skipped")),
                "offline": safe_text(row.get("offline")),
                "incognito_mode": safe_text(row.get("incognito_mode")),
            }
        )

    return fine_rows


def build_outputs(*, input_csv: Path, output_dir: Path) -> dict[str, Any]:
    if not input_csv.is_file():
        raise FileNotFoundError(f"Processed Spotify input not found: {input_csv}")

    fine_rows = build_rows(load_rows(input_csv))

    csv_output = output_dir / "fine_spotify_streaming_local.csv"
    jsonl_output = output_dir / "fine_spotify_streaming_local.jsonl"

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
