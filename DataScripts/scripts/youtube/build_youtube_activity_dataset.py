#!/usr/bin/env python3
"""Build per-account and merged YouTube activity datasets from account-specific exports."""

from __future__ import annotations

import argparse
import csv
import importlib.util
import json
from pathlib import Path
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_RAW_DIR = REPO_ROOT / "data_local" / "raw"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "data_local" / "processed"
ACCOUNT_PREFIX = "youtube_account_"
DEFAULT_LINES_PER_CHUNK = 1000

ACTIVITY_KEY_FIELDS = (
    "service",
    "action",
    "timestamp_iso",
    "primary_url",
    "primary_text",
    "secondary_text",
    "detail_text",
)

BASE_CSV_FIELDS = [
    "activity_id",
    "source_activity_id",
    "account_email",
    "source_kind",
    "source_file",
    "used_legacy_fallback",
    "service",
    "action",
    "timestamp_text",
    "timestamp_iso",
    "detail_text",
    "primary_text",
    "primary_url",
    "secondary_text",
    "secondary_url",
    "body_text",
    "body_link_count",
    "right_cell_text",
    "caption_text",
    "products_text",
    "why_is_this_here_text",
]

JSON_FIELD_MAP = {
    "detail_lines_json": "detail_lines",
    "body_lines_json": "body_lines",
    "body_links_json": "body_links",
    "right_cell_links_json": "right_cell_links",
    "caption_sections_json": "caption_sections",
    "content_cells_json": "content_cells",
}

SCALAR_TYPES = (str, int, float, bool)


def load_converter_module() -> Any:
    converter_path = SCRIPT_DIR / "convert_my_activity.py"
    spec = importlib.util.spec_from_file_location("convert_my_activity", converter_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load converter module from {converter_path}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


CONVERTER = load_converter_module()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build merged YouTube activity datasets from account-specific exports."
    )
    parser.add_argument(
        "--raw-dir",
        default=str(DEFAULT_RAW_DIR),
        help="Directory that contains the raw YouTube export folders.",
    )
    parser.add_argument(
        "--output-dir",
        default=str(DEFAULT_OUTPUT_DIR),
        help="Directory where processed datasets will be written.",
    )
    parser.add_argument(
        "--lines-per-chunk",
        type=int,
        default=DEFAULT_LINES_PER_CHUNK,
        help="Number of JSONL records to write into each chunk file.",
    )
    parser.add_argument(
        "--legacy-path",
        default=str(DEFAULT_RAW_DIR / "youtube_legacy" / "MyActivity.html"),
        help="Optional legacy MyActivity.html export used as a fallback for uncovered records.",
    )
    parser.add_argument(
        "--skip-legacy-fallback",
        action="store_true",
        help="Ignore the legacy MyActivity.html export even if it exists.",
    )
    return parser.parse_args()


def parse_account_label(account_dir: Path) -> str:
    if account_dir.name.startswith(ACCOUNT_PREFIX):
        return account_dir.name[len(ACCOUNT_PREFIX) :].replace("_", ".")
    return account_dir.name


def activity_key(record: dict[str, Any]) -> tuple[str, ...]:
    return tuple(str(record.get(field, "") or "") for field in ACTIVITY_KEY_FIELDS)


def parse_activity_html(path: Path) -> list[dict[str, Any]]:
    html_text = path.read_text(encoding="utf-8")
    fragments = CONVERTER.iter_fragments(html_text)
    return [
        CONVERTER.parse_entry(index, fragment)
        for index, fragment in enumerate(fragments, start=1)
    ]


def parse_subscriptions_csv(path: Path, account_email: str) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    if not path.is_file():
        return rows

    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            rows.append(
                {
                    "account_email": account_email,
                    "source_file": str(path.resolve().relative_to(REPO_ROOT)),
                    "channel_id": row.get("Channel Id", "").strip(),
                    "channel_url": row.get("Channel Url", "").strip(),
                    "channel_title": row.get("Channel Title", "").strip(),
                }
            )
    return rows


def annotate_records(
    records: list[dict[str, Any]],
    *,
    account_email: str,
    source_kind: str,
    source_file: Path,
    used_legacy_fallback: bool = False,
) -> list[dict[str, Any]]:
    annotated: list[dict[str, Any]] = []
    relative_source = str(source_file.resolve().relative_to(REPO_ROOT))

    for record in records:
        enriched = dict(record)
        enriched["source_activity_id"] = enriched.get("activity_id")
        enriched["account_email"] = account_email
        enriched["source_kind"] = source_kind
        enriched["source_file"] = relative_source
        enriched["used_legacy_fallback"] = used_legacy_fallback
        annotated.append(enriched)

    return annotated


def dedupe_records(records: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], int]:
    deduped: list[dict[str, Any]] = []
    seen: set[tuple[str, ...]] = set()
    duplicate_count = 0

    for record in records:
        record_key = activity_key(record)
        if record_key in seen:
            duplicate_count += 1
            continue
        seen.add(record_key)
        deduped.append(record)

    return deduped, duplicate_count


def sort_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(records, key=lambda record: (record.get("timestamp_iso") or "", record.get("action") or ""))


def assign_activity_ids(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    assigned: list[dict[str, Any]] = []
    for index, record in enumerate(records, start=1):
        enriched = dict(record)
        enriched["activity_id"] = index
        assigned.append(enriched)
    return assigned


def flatten_record(record: dict[str, Any]) -> dict[str, Any]:
    flat = {field: record.get(field) for field in BASE_CSV_FIELDS}

    for output_key, source_key in JSON_FIELD_MAP.items():
        flat[output_key] = json.dumps(record.get(source_key, []), ensure_ascii=False)

    for key, value in record.items():
        if key in flat or key in JSON_FIELD_MAP.values() or key == "raw_html":
            continue
        if value is None or isinstance(value, SCALAR_TYPES):
            flat[key] = value
        elif isinstance(value, (list, dict)):
            flat[f"{key}_json"] = json.dumps(value, ensure_ascii=False)

    return flat


def write_activity_csv(records: list[dict[str, Any]], output_path: Path) -> None:
    flat_records = [flatten_record(record) for record in records]
    fieldnames: list[str] = []
    for record in flat_records:
        for key in record:
            if key not in fieldnames:
                fieldnames.append(key)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(flat_records)


def write_jsonl(records: list[dict[str, Any]], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def write_jsonl_chunks(
    records: list[dict[str, Any]],
    output_dir: Path,
    *,
    prefix: str,
    lines_per_file: int,
) -> int:
    if lines_per_file <= 0:
        raise ValueError("--lines-per-chunk must be greater than zero")

    output_dir.mkdir(parents=True, exist_ok=True)
    chunk_count = 0

    for start in range(0, len(records), lines_per_file):
        chunk_count += 1
        chunk_path = output_dir / f"{prefix}_part_{chunk_count:03d}.jsonl"
        chunk_records = records[start : start + lines_per_file]
        write_jsonl(chunk_records, chunk_path)

    return chunk_count


def write_subscriptions_csv(rows: list[dict[str, str]], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ["account_email", "source_file", "channel_id", "channel_url", "channel_title"]
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def summarize_overlap(
    legacy_records: list[dict[str, Any]],
    account_records_map: dict[str, list[dict[str, Any]]],
) -> tuple[str | None, float]:
    legacy_keys = {activity_key(record) for record in legacy_records}
    if not legacy_keys:
        return None, 0.0

    best_account: str | None = None
    best_overlap = 0.0
    for account_email, account_records in account_records_map.items():
        account_keys = {activity_key(record) for record in account_records}
        overlap = len(legacy_keys & account_keys) / len(legacy_keys)
        if overlap > best_overlap:
            best_account = account_email
            best_overlap = overlap

    return best_account, best_overlap


def merge_legacy_fallback(
    *,
    legacy_path: Path,
    account_records_map: dict[str, list[dict[str, Any]]],
) -> tuple[int, str | None, float]:
    if not legacy_path.is_file():
        return 0, None, 0.0

    legacy_records = annotate_records(
        parse_activity_html(legacy_path),
        account_email="",
        source_kind="legacy_my_activity",
        source_file=legacy_path,
        used_legacy_fallback=True,
    )

    best_account, overlap = summarize_overlap(legacy_records, account_records_map)
    if best_account is None or overlap < 0.50:
        return 0, best_account, overlap

    account_keys = {activity_key(record) for record in account_records_map[best_account]}
    fallback_records: list[dict[str, Any]] = []
    for record in legacy_records:
        if activity_key(record) in account_keys:
            continue
        enriched = dict(record)
        enriched["account_email"] = best_account
        fallback_records.append(enriched)

    account_records_map[best_account].extend(fallback_records)
    return len(fallback_records), best_account, overlap


def build_account_records(raw_dir: Path) -> tuple[dict[str, list[dict[str, Any]]], dict[str, list[dict[str, str]]]]:
    account_records_map: dict[str, list[dict[str, Any]]] = {}
    subscription_rows_map: dict[str, list[dict[str, str]]] = {}

    account_dirs = sorted(
        path for path in raw_dir.iterdir() if path.is_dir() and path.name.startswith(ACCOUNT_PREFIX)
    )
    if not account_dirs:
        raise FileNotFoundError(
            f"No {ACCOUNT_PREFIX}* directories found under {raw_dir}"
        )

    for account_dir in account_dirs:
        account_email = parse_account_label(account_dir)
        account_records: list[dict[str, Any]] = []

        watch_path = account_dir / "YouTube and YouTube Music" / "history" / "watch-history.html"
        search_path = account_dir / "YouTube and YouTube Music" / "history" / "search-history.html"
        subscriptions_path = (
            account_dir / "YouTube and YouTube Music" / "subscriptions" / "subscriptions.csv"
        )

        if watch_path.is_file():
            account_records.extend(
                annotate_records(
                    parse_activity_html(watch_path),
                    account_email=account_email,
                    source_kind="watch_history",
                    source_file=watch_path,
                )
            )

        if search_path.is_file():
            account_records.extend(
                annotate_records(
                    parse_activity_html(search_path),
                    account_email=account_email,
                    source_kind="search_history",
                    source_file=search_path,
                )
            )

        account_records_map[account_email] = account_records
        subscription_rows_map[account_email] = parse_subscriptions_csv(subscriptions_path, account_email)

    return account_records_map, subscription_rows_map


def dedupe_subscriptions(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    deduped: list[dict[str, str]] = []
    seen: set[tuple[str, str, str]] = set()

    for row in rows:
        row_key = (row["account_email"], row["channel_id"], row["channel_title"])
        if row_key in seen:
            continue
        seen.add(row_key)
        deduped.append(row)

    return deduped


def build_outputs(
    *,
    raw_dir: Path,
    output_dir: Path,
    legacy_path: Path,
    use_legacy_fallback: bool,
    lines_per_chunk: int,
) -> dict[str, Any]:
    account_records_map, subscription_rows_map = build_account_records(raw_dir)

    pre_dedupe_counts = {
        account_email: len(records) for account_email, records in account_records_map.items()
    }

    legacy_added_count = 0
    legacy_account: str | None = None
    legacy_overlap = 0.0
    if use_legacy_fallback:
        legacy_added_count, legacy_account, legacy_overlap = merge_legacy_fallback(
            legacy_path=legacy_path,
            account_records_map=account_records_map,
        )

    summary: dict[str, Any] = {
        "accounts": {},
        "legacy_fallback": {
            "path": str(legacy_path),
            "used": use_legacy_fallback and legacy_added_count > 0,
            "attached_account_email": legacy_account,
            "overlap_ratio": legacy_overlap,
            "added_records": legacy_added_count,
        },
    }

    combined_records: list[dict[str, Any]] = []
    combined_subscriptions: list[dict[str, str]] = []

    for account_email in sorted(account_records_map):
        raw_records = account_records_map[account_email]
        deduped_records, duplicate_count = dedupe_records(raw_records)
        sorted_records = sort_records(deduped_records)
        account_records = assign_activity_ids(sorted_records)

        combined_records.extend(account_records)
        combined_subscriptions.extend(subscription_rows_map.get(account_email, []))

        account_output_dir = output_dir / "accounts" / account_email
        write_activity_csv(account_records, account_output_dir / "youtube_activity.csv")
        write_jsonl(account_records, account_output_dir / "youtube_activity.jsonl")
        chunk_count = write_jsonl_chunks(
            account_records,
            account_output_dir / "chunks",
            prefix=account_email,
            lines_per_file=lines_per_chunk,
        )
        write_subscriptions_csv(
            dedupe_subscriptions(subscription_rows_map.get(account_email, [])),
            account_output_dir / "subscriptions.csv",
        )

        summary["accounts"][account_email] = {
            "raw_records_before_dedupe": pre_dedupe_counts[account_email],
            "duplicate_records_removed": duplicate_count,
            "final_activity_records": len(account_records),
            "subscription_rows": len(subscription_rows_map.get(account_email, [])),
            "chunk_count": chunk_count,
        }

    combined_records = assign_activity_ids(sort_records(combined_records))
    combined_subscriptions = dedupe_subscriptions(combined_subscriptions)

    combined_output_dir = output_dir / "combined"
    write_activity_csv(combined_records, combined_output_dir / "youtube_activity_merged.csv")
    write_jsonl(combined_records, combined_output_dir / "youtube_activity_merged.jsonl")
    write_jsonl_chunks(
        combined_records,
        combined_output_dir / "chunks",
        prefix="merged",
        lines_per_file=lines_per_chunk,
    )
    write_subscriptions_csv(combined_subscriptions, combined_output_dir / "subscriptions_merged.csv")

    summary["combined"] = {
        "activity_records": len(combined_records),
        "subscription_rows": len(combined_subscriptions),
    }

    summary_path = output_dir / "build_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return summary


def main() -> None:
    args = parse_args()
    raw_dir = Path(args.raw_dir)
    output_dir = Path(args.output_dir)
    legacy_path = Path(args.legacy_path)

    summary = build_outputs(
        raw_dir=raw_dir,
        output_dir=output_dir,
        legacy_path=legacy_path,
        use_legacy_fallback=not args.skip_legacy_fallback,
        lines_per_chunk=args.lines_per_chunk,
    )

    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
