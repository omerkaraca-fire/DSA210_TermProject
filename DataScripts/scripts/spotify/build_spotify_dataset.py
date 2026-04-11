#!/usr/bin/env python3
"""Build processed Spotify music-streaming outputs from extended history exports."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_RAW_DIR = REPO_ROOT / "data_local" / "raw"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "data_local" / "processed" / "spotify"
ACCOUNT_PREFIX = "spotify_account_"

OUTPUT_FIELDS = [
    "spotify_stream_id",
    "account_label",
    "account_stream_index",
    "source_kind",
    "source_file",
    "timestamp_end_utc",
    "timestamp_start_utc",
    "date_utc",
    "month_utc",
    "year_utc",
    "playback_platform",
    "ms_played",
    "minutes_played",
    "hours_played",
    "track_name",
    "artist_name",
    "album_name",
    "spotify_track_uri",
    "shuffle",
    "skipped",
    "offline",
    "incognito_mode",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build processed Spotify music-streaming CSV and JSONL outputs."
    )
    parser.add_argument(
        "--raw-dir",
        default=str(DEFAULT_RAW_DIR),
        help="Directory that contains the raw Spotify export folders.",
    )
    parser.add_argument(
        "--output-dir",
        default=str(DEFAULT_OUTPUT_DIR),
        help="Directory where processed Spotify outputs will be written.",
    )
    return parser.parse_args()


def safe_text(value: str | None) -> str:
    return (value or "").strip()


def bool_text(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if value in (None, ""):
        return ""
    lowered = str(value).strip().lower()
    if lowered in {"true", "false"}:
        return lowered
    return ""


def repo_relative_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def parse_account_label(account_dir: Path) -> str:
    if account_dir.name.startswith(ACCOUNT_PREFIX):
        return account_dir.name[len(ACCOUNT_PREFIX) :].replace("_", ".")
    return account_dir.name


def locate_streaming_history_dir(account_dir: Path) -> Path:
    candidate = account_dir / "Spotify Extended Streaming History"
    if candidate.is_dir():
        return candidate
    return account_dir


def discover_account_dirs(raw_dir: Path) -> list[Path]:
    return sorted(
        path
        for path in raw_dir.iterdir()
        if path.is_dir() and path.name.startswith(ACCOUNT_PREFIX)
    )


def parse_timestamp(value: str | None) -> datetime | None:
    text = safe_text(value)
    if not text:
        return None
    try:
        return datetime.fromisoformat(text.replace("Z", "+00:00")).astimezone(timezone.utc)
    except ValueError:
        return None


def format_timestamp(value: datetime | None) -> str:
    if value is None:
        return ""
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def normalize_ms_played(value: Any) -> int:
    if value in (None, "", False):
        return 0
    try:
        return max(int(value), 0)
    except (TypeError, ValueError):
        return 0


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


def date_range(rows: list[dict[str, str]], field: str) -> dict[str, str]:
    valid_dates = sorted(row[field] for row in rows if safe_text(row.get(field)))
    if not valid_dates:
        return {"min": "", "max": ""}
    return {"min": valid_dates[0], "max": valid_dates[-1]}


def load_music_rows(raw_dir: Path) -> tuple[list[dict[str, str]], dict[str, Any]]:
    if not raw_dir.is_dir():
        raise FileNotFoundError(f"Spotify raw directory not found: {raw_dir}")

    account_dirs = discover_account_dirs(raw_dir)
    if not account_dirs:
        raise FileNotFoundError(f"No Spotify account folders found in {raw_dir}")

    kept_rows: list[dict[str, Any]] = []
    kept_counter: Counter[str] = Counter()
    dropped_counter: Counter[str] = Counter()
    source_files: list[str] = []
    account_counts: Counter[str] = Counter()

    for account_dir in account_dirs:
        account_label = parse_account_label(account_dir)
        streaming_dir = locate_streaming_history_dir(account_dir)
        json_paths = sorted(streaming_dir.glob("Streaming_History_*.json"))
        if not json_paths:
            raise FileNotFoundError(f"No Spotify history JSON files found in {streaming_dir}")

        account_index = 0
        for path in json_paths:
            source_files.append(repo_relative_path(path))
            is_video_file = "Video" in path.name
            rows = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(rows, list):
                raise ValueError(f"Expected a list of rows in {path}")

            for raw_index, raw_row in enumerate(rows, start=1):
                if not isinstance(raw_row, dict):
                    dropped_counter["non_dict_row"] += 1
                    continue
                if is_video_file:
                    dropped_counter["video_row"] += 1
                    continue
                if raw_row.get("episode_name"):
                    dropped_counter["episode_row"] += 1
                    continue
                if raw_row.get("audiobook_title") or raw_row.get("audiobook_chapter_title"):
                    dropped_counter["audiobook_row"] += 1
                    continue

                track_name = safe_text(raw_row.get("master_metadata_track_name"))
                if not track_name:
                    dropped_counter["missing_track_name"] += 1
                    continue

                end_timestamp = parse_timestamp(raw_row.get("ts"))
                ms_played = normalize_ms_played(raw_row.get("ms_played"))
                start_timestamp = None
                if end_timestamp is not None:
                    start_timestamp = end_timestamp - timedelta(milliseconds=ms_played)

                account_index += 1
                kept_counter["music_audio_rows"] += 1
                account_counts[account_label] += 1
                kept_rows.append(
                    {
                        "_account_label": account_label,
                        "_sort_key": (
                            format_timestamp(end_timestamp),
                            repo_relative_path(path),
                            raw_index,
                        ),
                        "spotify_stream_id": "",
                        "account_label": account_label,
                        "account_stream_index": account_index,
                        "source_kind": "audio",
                        "source_file": repo_relative_path(path),
                        "timestamp_end_utc": format_timestamp(end_timestamp),
                        "timestamp_start_utc": format_timestamp(start_timestamp),
                        "date_utc": end_timestamp.date().isoformat() if end_timestamp else "",
                        "month_utc": end_timestamp.strftime("%Y-%m-01") if end_timestamp else "",
                        "year_utc": str(end_timestamp.year) if end_timestamp else "",
                        "playback_platform": safe_text(raw_row.get("platform")),
                        "ms_played": str(ms_played),
                        "minutes_played": f"{ms_played / 60000:.6f}",
                        "hours_played": f"{ms_played / 3600000:.6f}",
                        "track_name": track_name,
                        "artist_name": safe_text(raw_row.get("master_metadata_album_artist_name")),
                        "album_name": safe_text(raw_row.get("master_metadata_album_album_name")),
                        "spotify_track_uri": safe_text(raw_row.get("spotify_track_uri")),
                        "shuffle": bool_text(raw_row.get("shuffle")),
                        "skipped": bool_text(raw_row.get("skipped")),
                        "offline": bool_text(raw_row.get("offline")),
                        "incognito_mode": bool_text(raw_row.get("incognito_mode")),
                    }
                )

    kept_rows.sort(key=lambda row: row["_sort_key"])

    output_rows: list[dict[str, str]] = []
    for index, row in enumerate(kept_rows, start=1):
        row["spotify_stream_id"] = f"spotify_stream_{index:06d}"
        output_rows.append({field: str(row.get(field, "")) for field in OUTPUT_FIELDS})

    summary = {
        "account_count": len(account_counts),
        "account_row_counts": dict(account_counts),
        "kept_counts": dict(kept_counter),
        "dropped_counts": dict(dropped_counter),
        "source_file_count": len(set(source_files)),
        "source_files": sorted(set(source_files)),
    }
    return output_rows, summary


def build_outputs(*, raw_dir: Path, output_dir: Path) -> dict[str, Any]:
    rows, load_summary = load_music_rows(raw_dir)

    csv_output = output_dir / "spotify_streaming_history_processed.csv"
    jsonl_output = output_dir / "spotify_streaming_history_processed.jsonl"
    summary_output = output_dir / "build_summary.json"

    write_csv_rows(rows, OUTPUT_FIELDS, csv_output)
    write_jsonl_rows(rows, OUTPUT_FIELDS, jsonl_output)

    summary_payload = {
        "dataset": "spotify_streaming_history_processed",
        "scope": "music_focused_audio_only",
        "input_root": repo_relative_path(raw_dir),
        "row_count": len(rows),
        "date_range": date_range(rows, "date_utc"),
        "unique_track_count": len(
            {
                (
                    row["spotify_track_uri"],
                    row["track_name"],
                    row["artist_name"],
                    row["album_name"],
                )
                for row in rows
            }
        ),
        "files": {
            "csv": csv_output.name,
            "jsonl": jsonl_output.name,
            "summary": summary_output.name,
        },
        "schema": OUTPUT_FIELDS,
        **load_summary,
    }

    summary_output.parent.mkdir(parents=True, exist_ok=True)
    summary_output.write_text(
        json.dumps(summary_payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    return {
        "raw_dir": str(raw_dir),
        "output_dir": str(output_dir),
        "row_count": summary_payload["row_count"],
        "date_range": summary_payload["date_range"],
        "unique_track_count": summary_payload["unique_track_count"],
        "account_count": summary_payload["account_count"],
        "kept_counts": summary_payload["kept_counts"],
        "dropped_counts": summary_payload["dropped_counts"],
        "outputs": {
            "csv": str(csv_output),
            "jsonl": str(jsonl_output),
            "summary": str(summary_output),
        },
    }


def main() -> None:
    args = parse_args()
    summary = build_outputs(
        raw_dir=Path(args.raw_dir),
        output_dir=Path(args.output_dir),
    )
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
