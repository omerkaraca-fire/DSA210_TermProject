#!/usr/bin/env python3
"""Build local reusable YouTube fine_processed exports from processed YouTube tables."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_ACTIVITY_INPUT = REPO_ROOT / "data_local" / "processed" / "combined" / "youtube_activity_merged.csv"
DEFAULT_SUBSCRIPTIONS_INPUT = REPO_ROOT / "data_local" / "processed" / "combined" / "subscriptions_merged.csv"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "data_local" / "fine_processed"
DEFAULT_ACTIVITY_ROWS_PER_FILE = 5000

COMMON_ACTIVITY_FIELDS = [
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

COMMON_SUBSCRIPTION_FIELDS = COMMON_ACTIVITY_FIELDS


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build local fine_processed YouTube CSV and JSONL exports."
    )
    parser.add_argument(
        "--activity-input",
        default=str(DEFAULT_ACTIVITY_INPUT),
        help="Path to the processed merged YouTube activity CSV.",
    )
    parser.add_argument(
        "--subscriptions-input",
        default=str(DEFAULT_SUBSCRIPTIONS_INPUT),
        help="Path to the processed merged YouTube subscriptions CSV.",
    )
    parser.add_argument(
        "--output-dir",
        default=str(DEFAULT_OUTPUT_DIR),
        help="Directory where local fine_processed outputs will be written.",
    )
    parser.add_argument(
        "--activity-rows-per-file",
        type=int,
        default=DEFAULT_ACTIVITY_ROWS_PER_FILE,
        help="Number of activity records to write into each chunked CSV and JSONL file.",
    )
    return parser.parse_args()


def read_csv_rows(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def normalize_source_file(value: str) -> str:
    text = (value or "").strip()
    if not text:
        return ""

    path = Path(text)
    if path.is_absolute():
        try:
            return str(path.relative_to(REPO_ROOT))
        except ValueError:
            return text
    return text


def date_from_timestamp(value: str) -> str:
    text = (value or "").strip()
    if len(text) >= 10 and text[4] == "-" and text[7] == "-":
        return text[:10]
    return ""


def build_activity_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    fine_rows: list[dict[str, str]] = []

    for index, row in enumerate(rows, start=1):
        timestamp = (row.get("timestamp_iso") or "").strip()
        record_id = (row.get("activity_id") or "").strip() or f"youtube_activity_{index:06d}"

        fine_row = {
            "fine_platform": "youtube",
            "fine_table": "youtube_activity_local",
            "fine_record_id": record_id,
            "fine_account": (row.get("account_email") or "").strip(),
            "fine_source_file": normalize_source_file(row.get("source_file") or ""),
            "fine_time_start": timestamp,
            "fine_time_end": timestamp,
            "fine_time_granularity": "timestamp" if timestamp else "none",
            "fine_date": date_from_timestamp(timestamp),
        }
        fine_row.update(row)
        fine_rows.append(fine_row)

    return fine_rows


def build_subscription_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    fine_rows: list[dict[str, str]] = []

    for index, row in enumerate(rows, start=1):
        channel_id = (row.get("channel_id") or "").strip()
        record_id = channel_id or f"youtube_subscription_{index:06d}"

        fine_row = {
            "fine_platform": "youtube",
            "fine_table": "youtube_subscriptions_local",
            "fine_record_id": record_id,
            "fine_account": (row.get("account_email") or "").strip(),
            "fine_source_file": normalize_source_file(row.get("source_file") or ""),
            "fine_time_start": "",
            "fine_time_end": "",
            "fine_time_granularity": "none",
            "fine_date": "",
        }
        fine_row.update(row)
        fine_rows.append(fine_row)

    return fine_rows


def ordered_fieldnames(common_fields: list[str], input_fields: list[str]) -> list[str]:
    fieldnames = list(common_fields)
    for field in input_fields:
        if field not in fieldnames:
            fieldnames.append(field)
    return fieldnames


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


def chunk_rows(rows: list[dict[str, str]], rows_per_file: int) -> list[list[dict[str, str]]]:
    if rows_per_file <= 0:
        raise ValueError("--activity-rows-per-file must be greater than zero")
    return [rows[start : start + rows_per_file] for start in range(0, len(rows), rows_per_file)]


def write_chunked_csv_rows(
    rows: list[dict[str, str]],
    fieldnames: list[str],
    output_dir: Path,
    *,
    prefix: str,
    rows_per_file: int,
) -> int:
    chunked_rows = chunk_rows(rows, rows_per_file)
    output_dir.mkdir(parents=True, exist_ok=True)

    for index, chunk in enumerate(chunked_rows, start=1):
        output_path = output_dir / f"{prefix}_part_{index:03d}.csv"
        write_csv_rows(chunk, fieldnames, output_path)

    return len(chunked_rows)


def write_chunked_jsonl_rows(
    rows: list[dict[str, str]],
    fieldnames: list[str],
    output_dir: Path,
    *,
    prefix: str,
    rows_per_file: int,
) -> int:
    chunked_rows = chunk_rows(rows, rows_per_file)
    output_dir.mkdir(parents=True, exist_ok=True)

    for index, chunk in enumerate(chunked_rows, start=1):
        output_path = output_dir / f"{prefix}_part_{index:03d}.jsonl"
        write_jsonl_rows(chunk, fieldnames, output_path)

    return len(chunked_rows)


def build_outputs(
    *,
    activity_input: Path,
    subscriptions_input: Path,
    output_dir: Path,
    activity_rows_per_file: int,
) -> dict[str, Any]:
    if not activity_input.is_file():
        raise FileNotFoundError(f"Processed activity input not found: {activity_input}")
    if not subscriptions_input.is_file():
        raise FileNotFoundError(f"Processed subscriptions input not found: {subscriptions_input}")

    activity_fields, activity_rows = read_csv_rows(activity_input)
    subscriptions_fields, subscription_rows = read_csv_rows(subscriptions_input)

    fine_activity_rows = build_activity_rows(activity_rows)
    fine_subscription_rows = build_subscription_rows(subscription_rows)

    activity_output_fields = ordered_fieldnames(COMMON_ACTIVITY_FIELDS, activity_fields)
    subscriptions_output_fields = ordered_fieldnames(COMMON_SUBSCRIPTION_FIELDS, subscriptions_fields)

    activity_csv = output_dir / "fine_youtube_activity_local.csv"
    activity_jsonl = output_dir / "fine_youtube_activity_local.jsonl"
    subscriptions_csv = output_dir / "fine_youtube_subscriptions_local.csv"
    subscriptions_jsonl = output_dir / "fine_youtube_subscriptions_local.jsonl"
    activity_csv_chunks_dir = output_dir / "chunks" / "csv"
    activity_jsonl_chunks_dir = output_dir / "chunks" / "jsonl"

    write_csv_rows(fine_activity_rows, activity_output_fields, activity_csv)
    write_jsonl_rows(fine_activity_rows, activity_output_fields, activity_jsonl)
    write_csv_rows(fine_subscription_rows, subscriptions_output_fields, subscriptions_csv)
    write_jsonl_rows(fine_subscription_rows, subscriptions_output_fields, subscriptions_jsonl)
    activity_csv_chunk_count = write_chunked_csv_rows(
        fine_activity_rows,
        activity_output_fields,
        activity_csv_chunks_dir,
        prefix="fine_youtube_activity_local",
        rows_per_file=activity_rows_per_file,
    )
    activity_jsonl_chunk_count = write_chunked_jsonl_rows(
        fine_activity_rows,
        activity_output_fields,
        activity_jsonl_chunks_dir,
        prefix="fine_youtube_activity_local",
        rows_per_file=activity_rows_per_file,
    )

    summary = {
        "activity_input": str(activity_input),
        "subscriptions_input": str(subscriptions_input),
        "outputs": {
            "activity_csv": str(activity_csv),
            "activity_jsonl": str(activity_jsonl),
            "subscriptions_csv": str(subscriptions_csv),
            "subscriptions_jsonl": str(subscriptions_jsonl),
            "activity_csv_chunks_dir": str(activity_csv_chunks_dir),
            "activity_jsonl_chunks_dir": str(activity_jsonl_chunks_dir),
        },
        "row_counts": {
            "activity_rows": len(fine_activity_rows),
            "subscription_rows": len(fine_subscription_rows),
        },
        "chunking": {
            "activity_rows_per_file": activity_rows_per_file,
            "activity_csv_chunk_count": activity_csv_chunk_count,
            "activity_jsonl_chunk_count": activity_jsonl_chunk_count,
        },
    }

    summary_path = output_dir / "youtube_fine_processed_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return summary


def main() -> None:
    args = parse_args()
    summary = build_outputs(
        activity_input=Path(args.activity_input),
        subscriptions_input=Path(args.subscriptions_input),
        output_dir=Path(args.output_dir),
        activity_rows_per_file=args.activity_rows_per_file,
    )
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
