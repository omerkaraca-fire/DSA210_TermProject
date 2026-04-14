#!/usr/bin/env python3
"""Build a common-ground CSV layer under data/fine_data from existing processed data."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
import sys
from typing import Callable

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "data" / "fine_data"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
RAW_DIR = PROJECT_ROOT / "data" / "raw"

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.social_activity import load_chatgpt_activity, load_instagram_activity

COMMON_COLUMNS = [
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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build common-ground fine data CSV files.")
    parser.add_argument(
        "--output-dir",
        default=str(DEFAULT_OUTPUT_DIR),
        help="Directory where fine_data CSV files will be written.",
    )
    return parser.parse_args()


def read_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, keep_default_na=False, low_memory=False)


def format_temporal(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, pd.Timestamp):
        if pd.isna(value):
            return ""
        return value.isoformat()
    if isinstance(value, str):
        return value.strip()
    if pd.isna(value):  # type: ignore[arg-type]
        return ""
    return str(value)


def normalize_temporal_series(values: pd.Series) -> pd.Series:
    return values.map(format_temporal)


def relative_path_text(value: object) -> str:
    text = format_temporal(value)
    if not text:
        return ""
    path = Path(text)
    if path.is_absolute():
        try:
            return str(path.relative_to(PROJECT_ROOT))
        except ValueError:
            return text
    return text


def date_from_temporal(value: object) -> str:
    text = format_temporal(value)
    if not text:
        return ""
    if len(text) >= 10 and text[4] == "-" and text[7] == "-":
        return text[:10]
    for fmt in ("%m/%d/%y", "%m/%d/%Y"):
        parsed = pd.to_datetime(text, format=fmt, errors="coerce")
        if not pd.isna(parsed):
            return parsed.date().isoformat()
    parsed = pd.to_datetime(text, utc=False, errors="coerce")
    if pd.isna(parsed):
        return ""
    return parsed.date().isoformat()


def make_generated_ids(prefix: str, count: int) -> pd.Series:
    return pd.Series([f"{prefix}_{index:06d}" for index in range(1, count + 1)])


def resolve_series(
    frame: pd.DataFrame,
    value: str | Callable[[pd.DataFrame], pd.Series] | None,
    *,
    default_prefix: str,
) -> pd.Series:
    if callable(value):
        series = value(frame)
    elif value is None:
        series = pd.Series([""] * len(frame))
    elif value in frame.columns:
        series = frame[value]
    else:
        series = pd.Series([value] * len(frame))

    if len(series) != len(frame):
        raise ValueError(f"Resolved series length mismatch for {default_prefix}")
    return series.reset_index(drop=True)


def prepare_frame(
    frame: pd.DataFrame,
    *,
    platform: str,
    table: str,
    record_id: str | Callable[[pd.DataFrame], pd.Series] | None,
    account: str | Callable[[pd.DataFrame], pd.Series] | None,
    source_file: str | Callable[[pd.DataFrame], pd.Series] | None,
    time_start: str | Callable[[pd.DataFrame], pd.Series] | None,
    time_end: str | Callable[[pd.DataFrame], pd.Series] | None,
    time_granularity: str | Callable[[pd.DataFrame], pd.Series],
) -> pd.DataFrame:
    data = frame.copy().reset_index(drop=True)
    generated_ids = make_generated_ids(table, len(data))

    record_id_series = resolve_series(data, record_id, default_prefix=table)
    record_id_series = record_id_series.where(record_id_series.astype(str).str.len() > 0, generated_ids)

    account_series = resolve_series(data, account, default_prefix=table).map(format_temporal)
    source_series = resolve_series(data, source_file, default_prefix=table).map(relative_path_text)
    time_start_series = normalize_temporal_series(resolve_series(data, time_start, default_prefix=table))
    time_end_series = normalize_temporal_series(resolve_series(data, time_end, default_prefix=table))
    granularity_series = resolve_series(data, time_granularity, default_prefix=table).map(format_temporal)

    date_series = time_start_series.map(date_from_temporal)
    date_series = date_series.where(date_series.astype(str).str.len() > 0, time_end_series.map(date_from_temporal))

    common = pd.DataFrame(
        {
            "fine_platform": platform,
            "fine_table": table,
            "fine_record_id": record_id_series,
            "fine_account": account_series,
            "fine_source_file": source_series,
            "fine_time_start": time_start_series,
            "fine_time_end": time_end_series,
            "fine_time_granularity": granularity_series,
            "fine_date": date_series,
        }
    )
    return pd.concat([common, data], axis=1)


@dataclass
class TableSpec:
    output_name: str
    platform: str
    table: str
    row_grain: str
    recorded_as: str
    source_paths: list[str]
    omitted_notes: list[str]
    loader: Callable[[], pd.DataFrame]
    record_id: str | Callable[[pd.DataFrame], pd.Series] | None
    account: str | Callable[[pd.DataFrame], pd.Series] | None
    source_file: str | Callable[[pd.DataFrame], pd.Series] | None
    time_start: str | Callable[[pd.DataFrame], pd.Series] | None
    time_end: str | Callable[[pd.DataFrame], pd.Series] | None
    time_granularity: str | Callable[[pd.DataFrame], pd.Series]


def youtube_activity() -> pd.DataFrame:
    return read_csv(PROCESSED_DIR / "combined" / "youtube_activity_merged.csv")


def youtube_subscriptions() -> pd.DataFrame:
    return read_csv(PROCESSED_DIR / "combined" / "subscriptions_merged.csv")


def spotify_streams() -> pd.DataFrame:
    return read_csv(PROCESSED_DIR / "spotify" / "combined" / "spotify_stream_history_merged.csv")


def twitter_tweets() -> pd.DataFrame:
    return read_csv(PROCESSED_DIR / "twitter" / "combined" / "twitter_tweets_merged.csv")


def twitter_likes() -> pd.DataFrame:
    return read_csv(PROCESSED_DIR / "twitter" / "combined" / "twitter_likes_merged.csv")


def twitter_messages() -> pd.DataFrame:
    return read_csv(PROCESSED_DIR / "twitter" / "combined" / "twitter_messages_merged.csv")


def twitter_calls() -> pd.DataFrame:
    return read_csv(PROCESSED_DIR / "twitter" / "combined" / "twitter_calls_merged.csv")


def twitter_spaces() -> pd.DataFrame:
    return read_csv(PROCESSED_DIR / "twitter" / "combined" / "twitter_spaces_merged.csv")


def twitter_activity_events() -> pd.DataFrame:
    return read_csv(PROCESSED_DIR / "twitter" / "combined" / "twitter_activity_events_merged.csv")


def prime_watch_history() -> pd.DataFrame:
    return read_csv(PROCESSED_DIR / "prime_video" / "prime_video_watch_history.csv")


def prime_day_summary() -> pd.DataFrame:
    return read_csv(PROCESSED_DIR / "prime_video" / "prime_video_day_summary.csv")


def prime_parse_issues() -> pd.DataFrame:
    return read_csv(PROCESSED_DIR / "prime_video" / "prime_video_parse_issues.csv")


def netflix_viewing_history() -> pd.DataFrame:
    return read_csv(PROCESSED_DIR / "netflix" / "NetflixViewingHistory.csv")


def chatgpt_conversations() -> pd.DataFrame:
    frame, _ = load_chatgpt_activity(RAW_DIR / "chatgpt_export" / "chat.html")
    for column in frame.columns:
        if pd.api.types.is_datetime64_any_dtype(frame[column]):
            frame[column] = normalize_temporal_series(frame[column])
    return frame.fillna("")


def chatgpt_messages() -> pd.DataFrame:
    _, frame = load_chatgpt_activity(RAW_DIR / "chatgpt_export" / "chat.html")
    for column in frame.columns:
        if pd.api.types.is_datetime64_any_dtype(frame[column]):
            frame[column] = normalize_temporal_series(frame[column])
    return frame.fillna("")


def instagram_events() -> pd.DataFrame:
    frame, _ = load_instagram_activity(
        RAW_DIR / "instagram_export" / "your_instagram_activity"
    )
    for column in frame.columns:
        if pd.api.types.is_datetime64_any_dtype(frame[column]):
            frame[column] = normalize_temporal_series(frame[column])
    return frame.fillna("")


def instagram_threads() -> pd.DataFrame:
    _, frame = load_instagram_activity(
        RAW_DIR / "instagram_export" / "your_instagram_activity"
    )
    for column in frame.columns:
        if pd.api.types.is_datetime64_any_dtype(frame[column]):
            frame[column] = normalize_temporal_series(frame[column])
    return frame.fillna("")


def netflix_common_date(frame: pd.DataFrame) -> pd.Series:
    return frame["Date"].map(date_from_temporal)


def choose_twitter_account(frame: pd.DataFrame) -> pd.Series:
    if "account_email" in frame.columns:
        email = frame["account_email"].astype(str)
        username = frame["account_username"].astype(str) if "account_username" in frame.columns else ""
        return email.where(email.str.len() > 0, username)
    if "account_username" in frame.columns:
        return frame["account_username"].astype(str)
    return pd.Series([""] * len(frame))


TABLE_SPECS = [
    TableSpec(
        output_name="fine_youtube_activity.csv",
        platform="youtube",
        table="youtube_activity",
        row_grain="One merged Google My Activity row for YouTube.",
        recorded_as="Merged activity table from account-specific watch and search history plus uncovered legacy fallback rows.",
        source_paths=[
            "data/processed/combined/youtube_activity_merged.csv",
        ],
        omitted_notes=[
            "Per-account duplicate copies were omitted because the merged table already preserves account identity in `account_email`.",
            "JSONL chunk files and build summaries were omitted because they duplicate the same rows or only describe the build.",
        ],
        loader=youtube_activity,
        record_id="activity_id",
        account="account_email",
        source_file="source_file",
        time_start="timestamp_iso",
        time_end="timestamp_iso",
        time_granularity="timestamp",
    ),
    TableSpec(
        output_name="fine_youtube_subscriptions.csv",
        platform="youtube",
        table="youtube_subscriptions",
        row_grain="One merged subscription row.",
        recorded_as="Merged subscription lookup table from the two account exports.",
        source_paths=[
            "data/processed/combined/subscriptions_merged.csv",
        ],
        omitted_notes=[
            "Per-account duplicate copies were omitted because the merged table already preserves account identity in `account_email`.",
        ],
        loader=youtube_subscriptions,
        record_id=lambda frame: (
            frame["account_email"].astype(str)
            + "::"
            + frame["channel_id"].astype(str)
        ),
        account="account_email",
        source_file="source_file",
        time_start=None,
        time_end=None,
        time_granularity="none",
    ),
    TableSpec(
        output_name="fine_spotify_stream_history.csv",
        platform="spotify",
        table="spotify_stream_history",
        row_grain="One merged Spotify stream row.",
        recorded_as="Merged stream-level listening table preserving raw Spotify fields and non-behavioral normalization fields.",
        source_paths=[
            "data/processed/spotify/combined/spotify_stream_history_merged.csv",
        ],
        omitted_notes=[
            "Per-account duplicate copies were omitted because the merged table already preserves account identity in `account_email`.",
            "JSONL chunk files and build summaries were omitted because they duplicate the same rows or only describe the build.",
        ],
        loader=spotify_streams,
        record_id="stream_id",
        account="account_email",
        source_file="source_file",
        time_start="timestamp_start_utc",
        time_end="timestamp_end_utc",
        time_granularity="timestamp",
    ),
    TableSpec(
        output_name="fine_twitter_tweets.csv",
        platform="twitter",
        table="twitter_tweets",
        row_grain="One merged tweet or deleted-tweet row.",
        recorded_as="Merged tweet table from the Twitter archive.",
        source_paths=[
            "data/processed/twitter/combined/twitter_tweets_merged.csv",
        ],
        omitted_notes=[
            "Per-account duplicate copies were omitted because the merged table already preserves account identity.",
        ],
        loader=twitter_tweets,
        record_id="tweet_record_id",
        account=choose_twitter_account,
        source_file="source_file",
        time_start="created_at_utc",
        time_end="created_at_utc",
        time_granularity="timestamp",
    ),
    TableSpec(
        output_name="fine_twitter_likes.csv",
        platform="twitter",
        table="twitter_likes",
        row_grain="One merged liked-tweet reference row.",
        recorded_as="Merged likes inventory from the Twitter archive.",
        source_paths=[
            "data/processed/twitter/combined/twitter_likes_merged.csv",
        ],
        omitted_notes=[
            "Per-like timestamps are not available in the current archive, so `fine_time_start` and `fine_time_end` are intentionally left blank.",
        ],
        loader=twitter_likes,
        record_id="like_record_id",
        account=choose_twitter_account,
        source_file="source_file",
        time_start=None,
        time_end=None,
        time_granularity="none",
    ),
    TableSpec(
        output_name="fine_twitter_messages.csv",
        platform="twitter",
        table="twitter_messages",
        row_grain="One merged DM or group-DM event row.",
        recorded_as="Merged message-event table from Twitter direct messages and group messages.",
        source_paths=[
            "data/processed/twitter/combined/twitter_messages_merged.csv",
        ],
        omitted_notes=[
            "Per-account duplicate copies were omitted because the merged table already preserves account identity.",
        ],
        loader=twitter_messages,
        record_id="message_record_id",
        account=choose_twitter_account,
        source_file="source_file",
        time_start="created_at_utc",
        time_end="created_at_utc",
        time_granularity="timestamp",
    ),
    TableSpec(
        output_name="fine_twitter_calls.csv",
        platform="twitter",
        table="twitter_calls",
        row_grain="One merged call or call-session row.",
        recorded_as="Merged call table from Twitter DM call exports.",
        source_paths=[
            "data/processed/twitter/combined/twitter_calls_merged.csv",
        ],
        omitted_notes=[
            "The current archive contains zero rows in this table, but the schema is preserved as part of the common base layer.",
        ],
        loader=twitter_calls,
        record_id="call_record_id",
        account=choose_twitter_account,
        source_file="source_file",
        time_start="started_at_utc",
        time_end="ended_at_utc",
        time_granularity="interval",
    ),
    TableSpec(
        output_name="fine_twitter_spaces.csv",
        platform="twitter",
        table="twitter_spaces",
        row_grain="One merged Twitter Space metadata row.",
        recorded_as="Merged Space metadata table from the Twitter archive.",
        source_paths=[
            "data/processed/twitter/combined/twitter_spaces_merged.csv",
        ],
        omitted_notes=[
            "The current archive contains zero rows in this table, but the schema is preserved as part of the common base layer.",
        ],
        loader=twitter_spaces,
        record_id="space_record_id",
        account=choose_twitter_account,
        source_file="source_file",
        time_start="created_at_utc",
        time_end="ended_at_utc",
        time_granularity="interval",
    ),
    TableSpec(
        output_name="fine_twitter_activity_events.csv",
        platform="twitter",
        table="twitter_activity_events",
        row_grain="One merged timestamped activity event row.",
        recorded_as="Merged activity timeline already present in the processed layer, built from tweets, messages, calls, and spaces without behavioral assumptions.",
        source_paths=[
            "data/processed/twitter/combined/twitter_activity_events_merged.csv",
        ],
        omitted_notes=[
            "This table is already a structural recomposition of other Twitter tables, but it was kept because it is part of the current processed layer and remains assumption-free.",
        ],
        loader=twitter_activity_events,
        record_id="activity_id",
        account=choose_twitter_account,
        source_file="source_file",
        time_start="timestamp_utc",
        time_end="timestamp_utc",
        time_granularity="timestamp",
    ),
    TableSpec(
        output_name="fine_prime_video_watch_history.csv",
        platform="prime_video",
        table="prime_video_watch_history",
        row_grain="One inferred Prime Video watch-history row.",
        recorded_as="Row-level watch-history table already produced by the Prime Video parser.",
        source_paths=[
            "data/processed/prime_video/prime_video_watch_history.csv",
        ],
        omitted_notes=[
            "PDF page headers, footers, legal text, and other page noise were already removed by the existing parser before this fine layer.",
        ],
        loader=prime_watch_history,
        record_id="record_id",
        account=None,
        source_file="data/raw/prime_video/raw.txt",
        time_start="watch_date",
        time_end="watch_date",
        time_granularity="date",
    ),
    TableSpec(
        output_name="fine_prime_video_day_summary.csv",
        platform="prime_video",
        table="prime_video_day_summary",
        row_grain="One aggregated Prime Video day row.",
        recorded_as="Existing day-level processed summary kept as a supplementary fine table because it already exists in the processed layer.",
        source_paths=[
            "data/processed/prime_video/prime_video_day_summary.csv",
        ],
        omitted_notes=[
            "This is an aggregate table derived from watch history, not a raw-like event table.",
        ],
        loader=prime_day_summary,
        record_id=None,
        account=None,
        source_file="data/processed/prime_video/prime_video_watch_history.csv",
        time_start="watch_date",
        time_end="watch_date",
        time_granularity="date",
    ),
    TableSpec(
        output_name="fine_prime_video_parse_issues.csv",
        platform="prime_video",
        table="prime_video_parse_issues",
        row_grain="One parse-audit issue row.",
        recorded_as="Existing parse-audit table that documents ambiguities in the Prime Video reconstruction.",
        source_paths=[
            "data/processed/prime_video/prime_video_parse_issues.csv",
        ],
        omitted_notes=[
            "This is a quality-control table, not a usage-event table, but it was kept because it is part of the current processed layer.",
        ],
        loader=prime_parse_issues,
        record_id="issue_id",
        account=None,
        source_file="data/raw/prime_video/raw.txt",
        time_start="watch_date_guess",
        time_end="watch_date_guess",
        time_granularity=lambda frame: frame["watch_date_guess"].astype(str).map(
            lambda value: "date" if value else "none"
        ),
    ),
    TableSpec(
        output_name="fine_netflix_viewing_history.csv",
        platform="netflix",
        table="netflix_viewing_history",
        row_grain="One Netflix viewing-history row.",
        recorded_as="Direct CSV copy already stored under data/processed/netflix.",
        source_paths=[
            "data/processed/netflix/NetflixViewingHistory.csv",
        ],
        omitted_notes=[
            "No additional processed fields existed to preserve here; the fine layer only standardizes common columns and ISO day values.",
        ],
        loader=netflix_viewing_history,
        record_id=None,
        account=None,
        source_file="data/raw/netflix/NetflixViewingHistory.csv",
        time_start=netflix_common_date,
        time_end=netflix_common_date,
        time_granularity="date",
    ),
    TableSpec(
        output_name="fine_chatgpt_conversations.csv",
        platform="chatgpt",
        table="chatgpt_conversations",
        row_grain="One ChatGPT conversation summary row from the current processed representation.",
        recorded_as="Current notebook-derived conversation table materialized as CSV without session estimates.",
        source_paths=[
            "data/raw/chatgpt_export/chat.html",
        ],
        omitted_notes=[
            "The fine layer preserves the current processed conversation table, not the full raw mapping tree per conversation.",
            "Behavioral estimates such as session time are intentionally excluded from the CSV itself.",
        ],
        loader=chatgpt_conversations,
        record_id="conversation_id",
        account=None,
        source_file="data/raw/chatgpt_export/chat.html",
        time_start="conversation_create_time",
        time_end="conversation_update_time",
        time_granularity="interval",
    ),
    TableSpec(
        output_name="fine_chatgpt_messages.csv",
        platform="chatgpt",
        table="chatgpt_messages",
        row_grain="One ChatGPT visible-branch message row from the current processed representation.",
        recorded_as="Current notebook-derived message table materialized as CSV without session estimates.",
        source_paths=[
            "data/raw/chatgpt_export/chat.html",
        ],
        omitted_notes=[
            "The fine layer preserves the current processed visible-branch table, not every raw mapping node in the HTML export.",
            "Behavioral estimates such as session time are intentionally excluded from the CSV itself.",
        ],
        loader=chatgpt_messages,
        record_id="message_id",
        account=None,
        source_file="data/raw/chatgpt_export/chat.html",
        time_start="timestamp",
        time_end="timestamp",
        time_granularity=lambda frame: pd.Series(["timestamp"] * len(frame)),
    ),
    TableSpec(
        output_name="fine_instagram_events.csv",
        platform="instagram",
        table="instagram_events",
        row_grain="One normalized timestamped Instagram interaction row from the current processed representation.",
        recorded_as="Current notebook-derived event table materialized as CSV without session estimates.",
        source_paths=[
            "data/raw/instagram_export/your_instagram_activity",
        ],
        omitted_notes=[
            "The fine layer preserves the current normalized event table, not every raw nested object such as full media arrays or participant blobs.",
            "Behavioral estimates such as session time or engagement-ratio proxies are intentionally excluded from the CSV itself.",
        ],
        loader=instagram_events,
        record_id=None,
        account=None,
        source_file="source_path",
        time_start="timestamp",
        time_end="timestamp",
        time_granularity=lambda frame: pd.Series(["timestamp"] * len(frame)),
    ),
    TableSpec(
        output_name="fine_instagram_threads.csv",
        platform="instagram",
        table="instagram_threads",
        row_grain="One normalized Instagram message-thread summary row from the current processed representation.",
        recorded_as="Current notebook-derived thread summary table materialized as CSV without session estimates.",
        source_paths=[
            "data/raw/instagram_export/your_instagram_activity/messages",
        ],
        omitted_notes=[
            "This table is a thread-level summary and does not preserve every raw participant object or every raw message payload inline.",
        ],
        loader=instagram_threads,
        record_id="thread_id",
        account=None,
        source_file="data/raw/instagram_export/your_instagram_activity/messages",
        time_start="first_timestamp",
        time_end="last_timestamp",
        time_granularity="interval",
    ),
]


def render_column_list(columns: list[str]) -> str:
    return ", ".join(f"`{column}`" for column in columns)


def build_readme(metadata: list[dict[str, object]], output_dir: Path) -> None:
    lines: list[str] = []
    lines.append("# Fine Data")
    lines.append("")
    lines.append("This folder is the project’s common-ground CSV layer.")
    lines.append("")
    lines.append("It keeps the current structured datasets in one place without behavioral assumptions such as estimated session time, inferred screen time, or engagement-ratio proxies.")
    lines.append("")
    lines.append("The fine layer does allow structural normalization for common columns, specifically:")
    lines.append("")
    lines.append("- `fine_platform`: platform label")
    lines.append("- `fine_table`: logical table name inside the fine layer")
    lines.append("- `fine_record_id`: preserved record ID where available, otherwise a generated stable row ID")
    lines.append("- `fine_account`: account label where the source dataset has one")
    lines.append("- `fine_source_file`: provenance path to the raw or processed source")
    lines.append("- `fine_time_start`: exact temporal value available for the row without inventing missing clock time")
    lines.append("- `fine_time_end`: exact end temporal value for interval-like rows, otherwise the same as start or blank")
    lines.append("- `fine_time_granularity`: `timestamp`, `date`, `interval`, or `none`")
    lines.append("- `fine_date`: normalized day value when one can be read without inventing missing time")
    lines.append("")
    lines.append("A date-only row keeps a date-only value. Midnight timestamps are not invented for datasets that do not have clock time.")
    lines.append("")
    lines.append("## Files")
    lines.append("")

    for item in metadata:
        lines.append(f"### `{item['output_name']}`")
        lines.append("")
        lines.append(f"- Platform: `{item['platform']}`")
        lines.append(f"- Logical table: `{item['table']}`")
        lines.append(f"- Rows: `{item['row_count']}`")
        lines.append(f"- Row grain: {item['row_grain']}")
        lines.append(f"- Recorded as: {item['recorded_as']}")
        lines.append(f"- Source path(s): {', '.join(f'`{path}`' for path in item['source_paths'])}")
        lines.append(f"- Time span: `{item['time_span']}`")
        lines.append(f"- Columns: {render_column_list(item['columns'])}")
        lines.append("")

    lines.append("## What Was Omitted And Why")
    lines.append("")
    lines.append("The following items were intentionally not copied into `data/fine_data/`:")
    lines.append("")
    lines.append("- JSONL files and chunked JSONL files, because they duplicate the same records already stored here as CSV.")
    lines.append("- Build summary JSON files, because they describe processing runs rather than core analysis rows.")
    lines.append("- Per-account duplicate CSVs when a merged table already exists and already preserves account identity.")
    lines.append("- Notebook-only behavioral outputs such as estimated session hours, estimated active minutes, or any proxy time-spent calculations, because the fine layer is meant to be assumption-free.")
    lines.append("")
    lines.append("Dataset-specific omissions or reductions:")
    lines.append("")

    seen_notes: list[str] = []
    for item in metadata:
        for note in item["omitted_notes"]:
            if note not in seen_notes:
                seen_notes.append(note)
                lines.append(f"- {note}")

    lines.append("")
    lines.append("If a raw export contained transport noise rather than real analytical content, that noise was not carried over. Examples include:")
    lines.append("")
    lines.append("- Twitter JavaScript wrapper assignments around JSON payloads")
    lines.append("- Prime Video copied PDF page headers, legal footers, and navigation text")
    lines.append("- Raw duplicate shard boundaries already reconciled in the existing processed layer")
    lines.append("")
    (output_dir / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    metadata: list[dict[str, object]] = []

    for spec in TABLE_SPECS:
        raw_frame = spec.loader()
        fine_frame = prepare_frame(
            raw_frame,
            platform=spec.platform,
            table=spec.table,
            record_id=spec.record_id,
            account=spec.account,
            source_file=spec.source_file,
            time_start=spec.time_start,
            time_end=spec.time_end,
            time_granularity=spec.time_granularity,
        )

        output_path = output_dir / spec.output_name
        fine_frame.to_csv(output_path, index=False)

        non_empty_start = [value for value in fine_frame["fine_time_start"].astype(str) if value]
        non_empty_end = [value for value in fine_frame["fine_time_end"].astype(str) if value]
        if non_empty_start or non_empty_end:
            start_value = min(non_empty_start) if non_empty_start else min(non_empty_end)
            end_value = max(non_empty_end) if non_empty_end else max(non_empty_start)
            time_span = f"{start_value} -> {end_value}"
        else:
            time_span = "not available"

        metadata.append(
            {
                "output_name": spec.output_name,
                "platform": spec.platform,
                "table": spec.table,
                "row_count": len(fine_frame),
                "row_grain": spec.row_grain,
                "recorded_as": spec.recorded_as,
                "source_paths": spec.source_paths,
                "time_span": time_span,
                "columns": list(fine_frame.columns),
                "omitted_notes": spec.omitted_notes,
            }
        )

    build_readme(metadata, output_dir)

    print(f"Wrote {len(metadata)} fine_data CSV files to {output_dir}")


if __name__ == "__main__":
    main()
