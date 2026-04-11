#!/usr/bin/env python3
"""Build the Spotify public release and mirror it locally/publicly."""

from __future__ import annotations

import argparse
import csv
import filecmp
import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_INPUT = REPO_ROOT / "data_local" / "fine_processed" / "fine_spotify_streaming_local.csv"
DEFAULT_LOCAL_OUTPUT_DIR = REPO_ROOT / "data_local" / "adjusted_local" / "spotify_public"
DEFAULT_PUBLIC_OUTPUT_DIR = REPO_ROOT / "data_github" / "spotify_public"

OUTPUT_FIELDS = [
    "fine_platform",
    "fine_table",
    "fine_record_id",
    "fine_account",
    "fine_source_file",
    "fine_time_start",
    "fine_time_end",
    "fine_time_granularity",
    "fine_date",
    "track_ref_id",
    "track_name",
    "artist_name",
    "album_name",
    "ms_played",
    "minutes_played",
    "hours_played",
]


class StableIdRegistry:
    def __init__(self) -> None:
        self._values: dict[str, dict[str, str]] = {}
        self._counts: dict[str, int] = {}

    def get_id(self, namespace: str, value: str) -> str:
        text = value.strip()
        if not text:
            return ""

        namespace_map = self._values.setdefault(namespace, {})
        if text in namespace_map:
            return namespace_map[text]

        next_index = self._counts.get(namespace, 0) + 1
        self._counts[namespace] = next_index
        identifier = f"{namespace}_{next_index:06d}"
        namespace_map[text] = identifier
        return identifier

    def namespace_size(self, namespace: str) -> int:
        return len(self._values.get(namespace, {}))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build the Spotify public release and mirror it to local/public outputs."
    )
    parser.add_argument(
        "--input-csv",
        default=str(DEFAULT_INPUT),
        help="Path to the local fine_processed Spotify CSV.",
    )
    parser.add_argument(
        "--local-output-dir",
        default=str(DEFAULT_LOCAL_OUTPUT_DIR),
        help="Directory where the local public mirror will be written.",
    )
    parser.add_argument(
        "--public-output-dir",
        default=str(DEFAULT_PUBLIC_OUTPUT_DIR),
        help="Directory where the public Spotify release will be written.",
    )
    return parser.parse_args()


def safe_text(value: str | None) -> str:
    return (value or "").strip()


def load_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def track_key(row: dict[str, str]) -> str:
    uri = safe_text(row.get("spotify_track_uri"))
    if uri:
        return f"uri::{uri}"
    return "name::{track}::{artist}::{album}".format(
        track=safe_text(row.get("track_name")),
        artist=safe_text(row.get("artist_name")),
        album=safe_text(row.get("album_name")),
    )


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


def write_summary(summary_payload: dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(summary_payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def date_range(rows: list[dict[str, str]]) -> dict[str, str]:
    valid_dates = sorted(row["fine_date"] for row in rows if safe_text(row.get("fine_date")))
    if not valid_dates:
        return {"min": "", "max": ""}
    return {"min": valid_dates[0], "max": valid_dates[-1]}


def build_public_rows(rows: list[dict[str, str]]) -> tuple[list[dict[str, str]], StableIdRegistry]:
    registry = StableIdRegistry()
    public_rows: list[dict[str, str]] = []

    for index, row in enumerate(rows, start=1):
        record_id = safe_text(row.get("fine_record_id")) or f"spotify_stream_{index:06d}"
        public_rows.append(
            {
                "fine_platform": "spotify",
                "fine_table": "spotify_streaming_public",
                "fine_record_id": record_id,
                "fine_account": registry.get_id("account", safe_text(row.get("fine_account"))),
                "fine_source_file": registry.get_id(
                    "source", safe_text(row.get("fine_source_file"))
                ),
                "fine_time_start": safe_text(row.get("fine_time_start")),
                "fine_time_end": safe_text(row.get("fine_time_end")),
                "fine_time_granularity": safe_text(row.get("fine_time_granularity")),
                "fine_date": safe_text(row.get("fine_date")),
                "track_ref_id": registry.get_id("track", track_key(row)),
                "track_name": safe_text(row.get("track_name")),
                "artist_name": safe_text(row.get("artist_name")),
                "album_name": safe_text(row.get("album_name")),
                "ms_played": safe_text(row.get("ms_played")),
                "minutes_played": safe_text(row.get("minutes_played")),
                "hours_played": safe_text(row.get("hours_played")),
            }
        )

    return public_rows, registry


def write_release(output_dir: Path, rows: list[dict[str, str]], summary_payload: dict[str, Any]) -> None:
    csv_output = output_dir / "spotify_streaming_public.csv"
    jsonl_output = output_dir / "spotify_streaming_public.jsonl"
    summary_output = output_dir / "spotify_public_summary.json"

    write_csv_rows(rows, OUTPUT_FIELDS, csv_output)
    write_jsonl_rows(rows, OUTPUT_FIELDS, jsonl_output)
    write_summary(summary_payload, summary_output)


def build_outputs(
    *,
    input_csv: Path,
    local_output_dir: Path,
    public_output_dir: Path,
) -> dict[str, Any]:
    if not input_csv.is_file():
        raise FileNotFoundError(f"Fine Spotify input not found: {input_csv}")

    public_rows, registry = build_public_rows(load_rows(input_csv))

    summary_payload = {
        "dataset": "spotify_streaming_public",
        "scope": "music_focused_audio_only",
        "row_count": len(public_rows),
        "date_range": date_range(public_rows),
        "account_reference_count": registry.namespace_size("account"),
        "source_file_reference_count": registry.namespace_size("source"),
        "track_reference_count": registry.namespace_size("track"),
        "files": {
            "csv": "spotify_streaming_public.csv",
            "jsonl": "spotify_streaming_public.jsonl",
            "summary": "spotify_public_summary.json",
        },
        "schema": OUTPUT_FIELDS,
    }

    write_release(local_output_dir, public_rows, summary_payload)
    write_release(public_output_dir, public_rows, summary_payload)

    mirrored_files = {
        "csv": (
            local_output_dir / "spotify_streaming_public.csv",
            public_output_dir / "spotify_streaming_public.csv",
        ),
        "jsonl": (
            local_output_dir / "spotify_streaming_public.jsonl",
            public_output_dir / "spotify_streaming_public.jsonl",
        ),
        "summary": (
            local_output_dir / "spotify_public_summary.json",
            public_output_dir / "spotify_public_summary.json",
        ),
    }

    return {
        "input_csv": str(input_csv),
        "local_output_dir": str(local_output_dir),
        "public_output_dir": str(public_output_dir),
        "row_count": summary_payload["row_count"],
        "date_range": summary_payload["date_range"],
        "account_reference_count": summary_payload["account_reference_count"],
        "source_file_reference_count": summary_payload["source_file_reference_count"],
        "track_reference_count": summary_payload["track_reference_count"],
        "mirrored_outputs_identical": all(
            filecmp.cmp(local_path, public_path, shallow=False)
            for local_path, public_path in mirrored_files.values()
        ),
        "outputs": {
            name: {
                "local": str(local_path),
                "public": str(public_path),
            }
            for name, (local_path, public_path) in mirrored_files.items()
        },
    }


def main() -> None:
    args = parse_args()
    summary = build_outputs(
        input_csv=Path(args.input_csv),
        local_output_dir=Path(args.local_output_dir),
        public_output_dir=Path(args.public_output_dir),
    )
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
