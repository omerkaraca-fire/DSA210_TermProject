#!/usr/bin/env python3
"""Build the anonymized YouTube public release and mirror it locally/publicly."""

from __future__ import annotations

import argparse
import csv
import json
import shutil
from pathlib import Path
from urllib.parse import parse_qs, urlparse


REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_ACTIVITY_INPUT = REPO_ROOT / "data_local" / "fine_processed" / "fine_youtube_activity_local.csv"
DEFAULT_SUBSCRIPTIONS_INPUT = (
    REPO_ROOT / "data_local" / "fine_processed" / "fine_youtube_subscriptions_local.csv"
)
DEFAULT_LOCAL_OUTPUT_DIR = REPO_ROOT / "data_local" / "adjusted_local" / "youtube_public"
DEFAULT_PUBLIC_OUTPUT_DIR = REPO_ROOT / "data_github" / "youtube_public"
DEFAULT_ACTIVITY_ROWS_PER_FILE = 5000

ACTIVITY_FIELDS = [
    "fine_platform",
    "fine_table",
    "fine_record_id",
    "fine_account",
    "fine_source_file",
    "fine_time_start",
    "fine_time_end",
    "fine_time_granularity",
    "fine_date",
    "source_kind",
    "used_legacy_fallback",
    "action",
    "target_ref_id",
    "target_kind",
    "target_url_kind",
    "channel_ref_id",
]

SUBSCRIPTION_FIELDS = [
    "fine_platform",
    "fine_table",
    "fine_record_id",
    "fine_account",
    "fine_source_file",
    "fine_time_start",
    "fine_time_end",
    "fine_time_granularity",
    "fine_date",
    "channel_ref_id",
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
        description="Build the anonymized YouTube public release and mirror it to local/public outputs."
    )
    parser.add_argument(
        "--activity-input",
        default=str(DEFAULT_ACTIVITY_INPUT),
        help="Path to the local fine_processed YouTube activity CSV.",
    )
    parser.add_argument(
        "--subscriptions-input",
        default=str(DEFAULT_SUBSCRIPTIONS_INPUT),
        help="Path to the local fine_processed YouTube subscriptions CSV.",
    )
    parser.add_argument(
        "--local-output-dir",
        default=str(DEFAULT_LOCAL_OUTPUT_DIR),
        help="Directory where the local public mirror will be written.",
    )
    parser.add_argument(
        "--public-output-dir",
        default=str(DEFAULT_PUBLIC_OUTPUT_DIR),
        help="Directory where the adjusted public release will be written.",
    )
    parser.add_argument(
        "--activity-rows-per-file",
        type=int,
        default=DEFAULT_ACTIVITY_ROWS_PER_FILE,
        help="Number of activity rows per chunked CSV/JSONL file.",
    )
    return parser.parse_args()


def load_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def safe_text(value: str | None) -> str:
    return (value or "").strip()


def date_from_timestamp(value: str) -> str:
    text = safe_text(value)
    if len(text) >= 10 and text[4] == "-" and text[7] == "-":
        return text[:10]
    return ""


def normalize_source_value(value: str) -> str:
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


def first_query_value(query: dict[str, list[str]], key: str) -> str:
    values = query.get(key, [])
    return safe_text(values[0]) if values else ""


def classify_url(url: str) -> tuple[str, str]:
    text = safe_text(url)
    if not text:
        return "", ""

    parsed = urlparse(text)
    domain = parsed.netloc.lower()
    path = parsed.path or ""

    if "youtube.com" not in domain and "youtu.be" not in domain:
        return domain or "unknown", "external"
    if "youtu.be" in domain:
        return "youtube", "shortlink"
    if path == "/watch":
        return "youtube", "watch"
    if path == "/results":
        return "youtube", "search_results"
    if path.startswith("/channel/"):
        return "youtube", "channel"
    if path.startswith("/shorts/"):
        return "youtube", "shorts"
    if path == "/playlist":
        return "youtube", "playlist"
    if path.startswith("/post/"):
        return "youtube", "post"
    if path.startswith("/@"):
        return "youtube", "handle"
    if path.startswith("/user/"):
        return "youtube", "user"
    if path.startswith("/c/"):
        return "youtube", "custom_channel"
    return "youtube", "other"


def normalize_url_key(url: str) -> str:
    # Canonicalize YouTube URLs so the same item/channel gets the same stable ID.
    text = safe_text(url)
    if not text:
        return ""

    parsed = urlparse(text)
    domain = parsed.netloc.lower().removeprefix("www.")
    path = parsed.path.rstrip("/")
    query = parse_qs(parsed.query)

    if domain.endswith("youtu.be"):
        video_id = safe_text(path.lstrip("/"))
        return f"youtube://watch/{video_id}" if video_id else "youtube://watch"

    if "youtube.com" in domain:
        if path == "/watch":
            video_id = first_query_value(query, "v")
            return f"youtube://watch/{video_id}" if video_id else "youtube://watch"
        if path == "/results":
            search_query = first_query_value(query, "search_query")
            return f"youtube://search/{search_query}" if search_query else "youtube://search"
        if path.startswith("/channel/"):
            channel_id = safe_text(path.split("/channel/", 1)[1])
            return f"youtube://channel/{channel_id}" if channel_id else "youtube://channel"
        if path.startswith("/shorts/"):
            shorts_id = safe_text(path.split("/shorts/", 1)[1])
            return f"youtube://shorts/{shorts_id}" if shorts_id else "youtube://shorts"
        if path == "/playlist":
            playlist_id = first_query_value(query, "list")
            return f"youtube://playlist/{playlist_id}" if playlist_id else "youtube://playlist"
        if path.startswith("/post/"):
            post_id = safe_text(path.split("/post/", 1)[1])
            return f"youtube://post/{post_id}" if post_id else "youtube://post"
        if path.startswith("/@"):
            handle = safe_text(path[2:])
            return f"youtube://handle/{handle}" if handle else "youtube://handle"
        if path.startswith("/user/"):
            user_name = safe_text(path.split("/user/", 1)[1])
            return f"youtube://user/{user_name}" if user_name else "youtube://user"
        if path.startswith("/c/"):
            channel_name = safe_text(path.split("/c/", 1)[1])
            return f"youtube://custom_channel/{channel_name}" if channel_name else "youtube://custom_channel"
        return f"youtube://path{path or '/'}"

    return f"{domain}{path}?{parsed.query}".rstrip("?")


def extract_channel_key(
    *,
    channel_id: str = "",
    channel_url: str = "",
    channel_title: str = "",
) -> str:
    normalized_channel_id = safe_text(channel_id)
    if normalized_channel_id:
        return f"channel_id::{normalized_channel_id}"

    normalized_url = normalize_url_key(channel_url)
    if normalized_url:
        if normalized_url.startswith("youtube://channel/"):
            normalized_channel_id = safe_text(normalized_url.split("youtube://channel/", 1)[1])
            if normalized_channel_id:
                return f"channel_id::{normalized_channel_id}"
        return f"channel_url::{normalized_url}"

    normalized_title = safe_text(channel_title)
    if normalized_title:
        return f"channel_title::{normalized_title}"

    return ""


def infer_target_kind(action: str, target_url_kind: str) -> str:
    if action == "Watched":
        return "video"
    if action == "Searched for":
        return "search_query"
    if action == "Subscribed to":
        return "channel"
    if action == "Liked":
        return "video"
    if action == "Viewed" and target_url_kind == "post":
        return "community_post"
    if action == "Viewed" and target_url_kind == "channel":
        return "channel"
    if action == "Used Shorts creation tools":
        return "shorts_tool"
    if action == "Answered survey question":
        return "survey_response"
    return "other"


def build_target_key(row: dict[str, str]) -> str:
    # Prefer URL-based identity, then fall back to text for non-link actions.
    primary_url = safe_text(row.get("primary_url"))
    primary_text = safe_text(row.get("primary_text"))
    detail_text = safe_text(row.get("detail_text"))
    action = safe_text(row.get("action"))

    normalized_url = normalize_url_key(primary_url)
    if normalized_url:
        return f"url::{normalized_url}"
    if primary_text:
        return f"text::{primary_text}"
    if detail_text:
        return f"detail::{detail_text}"
    if action:
        return f"action::{action}"
    return ""


def build_channel_key_from_activity(row: dict[str, str]) -> str:
    action = safe_text(row.get("action"))
    secondary_url = safe_text(row.get("secondary_url"))
    secondary_text = safe_text(row.get("secondary_text"))
    primary_url = safe_text(row.get("primary_url"))
    primary_text = safe_text(row.get("primary_text"))

    _, secondary_kind = classify_url(secondary_url)
    if secondary_url or secondary_text:
        return extract_channel_key(
            channel_url=secondary_url if secondary_kind in {"channel", "handle", "user", "custom_channel"} else "",
            channel_title=secondary_text,
        )

    _, primary_kind = classify_url(primary_url)
    if action == "Subscribed to":
        return extract_channel_key(
            channel_url=primary_url if primary_kind in {"channel", "handle", "user", "custom_channel"} else "",
            channel_title=primary_text,
        )

    return ""


def sanitize_activity_row(registry: StableIdRegistry, row: dict[str, str]) -> dict[str, str]:
    action = safe_text(row.get("action"))
    primary_url = safe_text(row.get("primary_url"))
    _, target_url_kind = classify_url(primary_url)
    target_kind = infer_target_kind(action, target_url_kind)
    target_key = build_target_key(row)
    channel_key = build_channel_key_from_activity(row)
    channel_ref_id = registry.get_id("channel_ref", channel_key)

    if target_kind == "channel" and channel_ref_id:
        target_ref_id = channel_ref_id
    else:
        target_ref_id = registry.get_id("target_ref", target_key)

    fine_time_start = safe_text(row.get("fine_time_start") or row.get("timestamp_iso"))
    fine_time_end = safe_text(row.get("fine_time_end") or fine_time_start)
    fine_time_granularity = safe_text(
        row.get("fine_time_granularity") or ("timestamp" if fine_time_start else "none")
    )
    fine_date = safe_text(row.get("fine_date") or date_from_timestamp(fine_time_start))

    return {
        "fine_platform": safe_text(row.get("fine_platform")) or "youtube",
        "fine_table": "youtube_activity_public",
        "fine_record_id": safe_text(row.get("fine_record_id") or row.get("activity_id")),
        "fine_account": registry.get_id(
            "account_ref", safe_text(row.get("fine_account") or row.get("account_email"))
        ),
        "fine_source_file": registry.get_id(
            "source_file_ref",
            normalize_source_value(safe_text(row.get("fine_source_file") or row.get("source_file"))),
        ),
        "fine_time_start": fine_time_start,
        "fine_time_end": fine_time_end,
        "fine_time_granularity": fine_time_granularity,
        "fine_date": fine_date,
        "source_kind": safe_text(row.get("source_kind")),
        "used_legacy_fallback": safe_text(row.get("used_legacy_fallback")),
        "action": action,
        "target_ref_id": target_ref_id,
        "target_kind": target_kind,
        "target_url_kind": target_url_kind,
        "channel_ref_id": channel_ref_id,
    }


def sanitize_subscription_row(registry: StableIdRegistry, row: dict[str, str]) -> dict[str, str]:
    fine_account = registry.get_id(
        "account_ref", safe_text(row.get("fine_account") or row.get("account_email"))
    )
    channel_key = extract_channel_key(
        channel_id=safe_text(row.get("channel_id")),
        channel_url=safe_text(row.get("channel_url")),
        channel_title=safe_text(row.get("channel_title")),
    )
    channel_ref_id = registry.get_id("channel_ref", channel_key)

    return {
        "fine_platform": safe_text(row.get("fine_platform")) or "youtube",
        "fine_table": "youtube_subscriptions_public",
        "fine_record_id": f"{fine_account}::{channel_ref_id}" if fine_account and channel_ref_id else "",
        "fine_account": fine_account,
        "fine_source_file": registry.get_id(
            "source_file_ref",
            normalize_source_value(safe_text(row.get("fine_source_file") or row.get("source_file"))),
        ),
        "fine_time_start": "",
        "fine_time_end": "",
        "fine_time_granularity": "none",
        "fine_date": "",
        "channel_ref_id": channel_ref_id,
    }


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
            ordered = {field: row.get(field, "") for field in fieldnames}
            handle.write(json.dumps(ordered, ensure_ascii=False) + "\n")


def chunk_rows(rows: list[dict[str, str]], rows_per_file: int) -> list[list[dict[str, str]]]:
    if rows_per_file <= 0:
        raise ValueError("--activity-rows-per-file must be greater than zero")
    return [rows[start : start + rows_per_file] for start in range(0, len(rows), rows_per_file)]


def clear_output_dir(output_dir: Path) -> None:
    if output_dir.exists():
        chunks_dir = output_dir / "chunks"
        if chunks_dir.exists():
            shutil.rmtree(chunks_dir)

        for file_name in [
            "youtube_activity_public.csv",
            "youtube_activity_public.jsonl",
            "youtube_subscriptions_public.csv",
            "youtube_subscriptions_public.jsonl",
            "youtube_activity_adjusted.csv",
            "youtube_activity_adjusted.jsonl",
            "youtube_subscriptions_adjusted.csv",
            "youtube_subscriptions_adjusted.jsonl",
            "youtube_public_summary.json",
        ]:
            file_path = output_dir / file_name
            if file_path.exists():
                file_path.unlink()


def write_activity_chunks(
    rows: list[dict[str, str]],
    fieldnames: list[str],
    output_dir: Path,
    *,
    rows_per_file: int,
) -> list[dict[str, object]]:
    chunk_summaries: list[dict[str, object]] = []
    chunked_rows = chunk_rows(rows, rows_per_file)
    csv_output_dir = output_dir / "chunks" / "csv"
    jsonl_output_dir = output_dir / "chunks" / "jsonl"

    for index, chunk in enumerate(chunked_rows, start=1):
        csv_output_path = csv_output_dir / f"youtube_activity_public_part_{index:03d}.csv"
        jsonl_output_path = jsonl_output_dir / f"youtube_activity_public_part_{index:03d}.jsonl"
        write_csv_rows(chunk, fieldnames, csv_output_path)
        write_jsonl_rows(chunk, fieldnames, jsonl_output_path)
        chunk_summaries.append(
            {
                "output_csv": str(csv_output_path.relative_to(REPO_ROOT)),
                "output_jsonl": str(jsonl_output_path.relative_to(REPO_ROOT)),
                "row_count": len(chunk),
            }
        )

    return chunk_summaries


def build_release_rows(
    *,
    activity_input: Path,
    subscriptions_input: Path,
) -> tuple[list[dict[str, str]], list[dict[str, str]], StableIdRegistry]:
    if not activity_input.is_file():
        raise FileNotFoundError(f"Activity input not found: {activity_input}")
    if not subscriptions_input.is_file():
        raise FileNotFoundError(f"Subscriptions input not found: {subscriptions_input}")

    registry = StableIdRegistry()
    activity_rows = [sanitize_activity_row(registry, row) for row in load_rows(activity_input)]
    subscription_rows = [sanitize_subscription_row(registry, row) for row in load_rows(subscriptions_input)]
    return activity_rows, subscription_rows, registry


def write_release_outputs(
    *,
    activity_rows: list[dict[str, str]],
    subscription_rows: list[dict[str, str]],
    output_dir: Path,
    activity_rows_per_file: int,
    registry: StableIdRegistry,
) -> dict[str, object]:
    # Rebuild the release from scratch so stale files do not remain beside new names.
    clear_output_dir(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    activity_csv = output_dir / "youtube_activity_public.csv"
    activity_jsonl = output_dir / "youtube_activity_public.jsonl"
    subscriptions_csv = output_dir / "youtube_subscriptions_public.csv"
    subscriptions_jsonl = output_dir / "youtube_subscriptions_public.jsonl"

    write_csv_rows(activity_rows, ACTIVITY_FIELDS, activity_csv)
    write_jsonl_rows(activity_rows, ACTIVITY_FIELDS, activity_jsonl)
    write_csv_rows(subscription_rows, SUBSCRIPTION_FIELDS, subscriptions_csv)
    write_jsonl_rows(subscription_rows, SUBSCRIPTION_FIELDS, subscriptions_jsonl)
    chunk_summaries = write_activity_chunks(
        activity_rows,
        ACTIVITY_FIELDS,
        output_dir,
        rows_per_file=activity_rows_per_file,
    )

    summary = {
        "output_dir": str(output_dir),
        "row_counts": {
            "activity_rows": len(activity_rows),
            "subscription_rows": len(subscription_rows),
        },
        "unique_id_counts": {
            "account_ids": registry.namespace_size("account_ref"),
            "source_file_ids": registry.namespace_size("source_file_ref"),
            "target_ref_ids": registry.namespace_size("target_ref"),
            "channel_ref_ids": registry.namespace_size("channel_ref"),
        },
        "outputs": {
            "activity_csv": str(activity_csv.relative_to(REPO_ROOT)),
            "activity_jsonl": str(activity_jsonl.relative_to(REPO_ROOT)),
            "subscriptions_csv": str(subscriptions_csv.relative_to(REPO_ROOT)),
            "subscriptions_jsonl": str(subscriptions_jsonl.relative_to(REPO_ROOT)),
        },
        "chunking": {
            "activity_rows_per_file": activity_rows_per_file,
            "activity_chunk_count": len(chunk_summaries),
            "chunks": chunk_summaries,
        },
        "schemas": {
            "activity_fields": ACTIVITY_FIELDS,
            "subscription_fields": SUBSCRIPTION_FIELDS,
        },
    }

    summary_path = output_dir / "youtube_public_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return summary


def build_outputs(
    *,
    activity_input: Path,
    subscriptions_input: Path,
    local_output_dir: Path,
    public_output_dir: Path,
    activity_rows_per_file: int,
) -> dict[str, object]:
    activity_rows, subscription_rows, registry = build_release_rows(
        activity_input=activity_input,
        subscriptions_input=subscriptions_input,
    )

    local_summary = write_release_outputs(
        activity_rows=activity_rows,
        subscription_rows=subscription_rows,
        output_dir=local_output_dir,
        activity_rows_per_file=activity_rows_per_file,
        registry=registry,
    )
    public_summary = write_release_outputs(
        activity_rows=activity_rows,
        subscription_rows=subscription_rows,
        output_dir=public_output_dir,
        activity_rows_per_file=activity_rows_per_file,
        registry=registry,
    )

    return {
        "activity_input": str(activity_input),
        "subscriptions_input": str(subscriptions_input),
        "local_output": local_summary,
        "public_output": public_summary,
    }


def main() -> None:
    args = parse_args()
    summary = build_outputs(
        activity_input=Path(args.activity_input),
        subscriptions_input=Path(args.subscriptions_input),
        local_output_dir=Path(args.local_output_dir),
        public_output_dir=Path(args.public_output_dir),
        activity_rows_per_file=args.activity_rows_per_file,
    )
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
