#!/usr/bin/env python3
"""Build processed Twitter datasets from archive wrapper files."""

from __future__ import annotations

import argparse
import csv
import html
import json
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_RAW_DIR = PROJECT_ROOT / "data" / "raw" / "twitter_archive"
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "data" / "processed" / "twitter"
DEFAULT_LINES_PER_CHUNK = 1000

TWEET_FIELDS = [
    "tweet_record_id",
    "account_username",
    "account_id",
    "account_email",
    "account_display_name",
    "source_file",
    "is_deleted",
    "tweet_id",
    "created_at_utc",
    "deleted_at_utc",
    "tweet_type",
    "source_app",
    "language",
    "full_text",
    "favorite_count",
    "retweet_count",
    "favorited",
    "retweeted",
    "url_count",
    "mention_count",
    "hashtag_count",
    "expanded_urls_json",
    "mentioned_screen_names_json",
]

LIKE_FIELDS = [
    "like_record_id",
    "account_username",
    "account_id",
    "account_email",
    "account_display_name",
    "source_file",
    "tweet_id",
    "full_text",
    "expanded_url",
    "has_timestamp",
]

MESSAGE_FIELDS = [
    "message_record_id",
    "account_username",
    "account_id",
    "account_email",
    "account_display_name",
    "source_file",
    "conversation_id",
    "conversation_type",
    "event_type",
    "event_id",
    "created_at_utc",
    "sender_id",
    "recipient_id",
    "initiating_user_id",
    "text",
    "url_count",
    "media_url_count",
    "reaction_count",
    "participant_count",
    "participant_user_ids_json",
    "urls_json",
    "media_urls_json",
]

CALL_FIELDS = [
    "call_record_id",
    "account_username",
    "account_id",
    "account_email",
    "account_display_name",
    "source_file",
    "call_kind",
    "host_broadcast_id",
    "conversation_id",
    "created_at_utc",
    "started_at_utc",
    "published_at_utc",
    "ended_at_utc",
    "end_reason",
    "twitter_user_id",
    "invitee_user_ids_json",
    "exact_duration_minutes",
]

SPACE_FIELDS = [
    "space_record_id",
    "account_username",
    "account_id",
    "account_email",
    "account_display_name",
    "source_file",
    "space_id",
    "creator_user_id",
    "created_at_utc",
    "ended_at_utc",
    "exact_duration_minutes",
    "total_participating",
    "total_participated",
    "speaker_count",
]

EVENT_FIELDS = [
    "activity_id",
    "account_username",
    "account_id",
    "account_email",
    "account_display_name",
    "source_dataset",
    "source_file",
    "event_type",
    "timestamp_utc",
    "primary_id",
    "conversation_id",
    "text",
    "source_app",
    "url_count",
    "media_count",
    "exact_duration_minutes",
    "is_deleted_tweet",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build processed Twitter datasets.")
    parser.add_argument(
        "--raw-dir",
        default=str(DEFAULT_RAW_DIR),
        help="Directory that contains one or more Twitter archive folders.",
    )
    parser.add_argument(
        "--output-dir",
        default=str(DEFAULT_OUTPUT_DIR),
        help="Directory where processed Twitter outputs will be written.",
    )
    parser.add_argument(
        "--lines-per-chunk",
        type=int,
        default=DEFAULT_LINES_PER_CHUNK,
        help="Number of JSONL records per event chunk file.",
    )
    return parser.parse_args()


def discover_archives(raw_dir: Path) -> list[Path]:
    return sorted(
        path
        for path in raw_dir.iterdir()
        if path.is_dir() and (path / "data" / "account.js").is_file()
    )


def load_wrapped_js(path: Path) -> Any:
    text = path.read_text(encoding="utf-8")
    if " = " not in text:
        raise ValueError(f"Expected wrapper assignment in {path}")
    return json.loads(text.split(" = ", 1)[1])


def parse_timestamp(value: str | None) -> datetime | None:
    if not value:
        return None

    formats = [
        "%a %b %d %H:%M:%S %z %Y",
        "%Y-%m-%dT%H:%M:%S.%fZ",
        "%Y-%m-%dT%H:%M:%SZ",
    ]
    for fmt in formats:
        try:
            parsed = datetime.strptime(value, fmt)
            if parsed.tzinfo is None:
                parsed = parsed.replace(tzinfo=timezone.utc)
            return parsed.astimezone(timezone.utc)
        except ValueError:
            continue

    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)
    except ValueError:
        return None


def format_timestamp(value: datetime | None) -> str:
    if value is None:
        return ""
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def normalize_bool(value: Any) -> bool | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered == "true":
            return True
        if lowered == "false":
            return False
    return None


def normalize_int(value: Any) -> int | None:
    if value in (None, ""):
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def strip_html_anchor(value: str | None) -> str:
    if not value:
        return ""
    return html.unescape(re.sub(r"<[^>]+>", "", value)).strip()


def json_text(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False)


def relative_to_project(path: Path) -> str:
    return str(path.relative_to(PROJECT_ROOT))


def write_csv(rows: list[dict[str, Any]], fieldnames: list[str], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_jsonl(rows: list[dict[str, Any]], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def write_jsonl_chunks(
    rows: list[dict[str, Any]],
    output_dir: Path,
    *,
    prefix: str,
    lines_per_file: int,
) -> int:
    if lines_per_file <= 0:
        raise ValueError("--lines-per-chunk must be greater than zero")

    output_dir.mkdir(parents=True, exist_ok=True)
    chunk_count = 0
    for start in range(0, len(rows), lines_per_file):
        chunk_count += 1
        chunk_path = output_dir / f"{prefix}_part_{chunk_count:03d}.jsonl"
        write_jsonl(rows[start : start + lines_per_file], chunk_path)
    return chunk_count


def sort_by_timestamp(rows: list[dict[str, Any]], timestamp_field: str) -> list[dict[str, Any]]:
    return sorted(rows, key=lambda row: (row.get(timestamp_field) or "", row.get("primary_id") or row.get("tweet_id") or row.get("event_id") or ""))


def parse_account_metadata(data_dir: Path) -> dict[str, Any]:
    account_rows = load_wrapped_js(data_dir / "account.js")
    account = account_rows[0]["account"] if account_rows else {}
    return {
        "account_username": account.get("username") or "twitter_account",
        "account_id": account.get("accountId") or "",
        "account_email": account.get("email") or "",
        "account_display_name": account.get("accountDisplayName") or "",
        "account_created_at_utc": format_timestamp(parse_timestamp(account.get("createdAt"))),
        "account_created_via": account.get("createdVia") or "",
    }


def parse_tweets(
    archive_dir: Path,
    account: dict[str, Any],
) -> list[dict[str, Any]]:
    data_dir = archive_dir / "data"
    rows: list[dict[str, Any]] = []

    for file_name, is_deleted in (("tweets.js", False), ("deleted-tweets.js", True)):
        source_path = data_dir / file_name
        source_rows = load_wrapped_js(source_path)
        for index, item in enumerate(source_rows, start=1):
            tweet = item.get("tweet", {})
            entities = tweet.get("entities") or {}
            urls = entities.get("urls") or []
            mentions = entities.get("user_mentions") or []
            hashtags = entities.get("hashtags") or []
            full_text = tweet.get("full_text") or ""
            tweet_type = "retweet" if full_text.startswith("RT @") else "tweet"
            rows.append(
                {
                    "tweet_record_id": f"{account['account_username']}_tweet_{len(rows) + 1:06d}",
                    "account_username": account["account_username"],
                    "account_id": account["account_id"],
                    "account_email": account["account_email"],
                    "account_display_name": account["account_display_name"],
                    "source_file": relative_to_project(source_path),
                    "is_deleted": is_deleted,
                    "tweet_id": tweet.get("id_str") or tweet.get("id") or f"{file_name}_{index}",
                    "created_at_utc": format_timestamp(parse_timestamp(tweet.get("created_at"))),
                    "deleted_at_utc": format_timestamp(parse_timestamp(tweet.get("deleted_at"))),
                    "tweet_type": "deleted_retweet" if is_deleted and tweet_type == "retweet" else ("deleted_tweet" if is_deleted else tweet_type),
                    "source_app": strip_html_anchor(tweet.get("source")),
                    "language": tweet.get("lang") or "",
                    "full_text": full_text,
                    "favorite_count": normalize_int(tweet.get("favorite_count")),
                    "retweet_count": normalize_int(tweet.get("retweet_count")),
                    "favorited": normalize_bool(tweet.get("favorited")),
                    "retweeted": normalize_bool(tweet.get("retweeted")),
                    "url_count": len(urls),
                    "mention_count": len(mentions),
                    "hashtag_count": len(hashtags),
                    "expanded_urls_json": json_text([url.get("expanded_url") or url.get("expanded") or "" for url in urls]),
                    "mentioned_screen_names_json": json_text([mention.get("screen_name") or "" for mention in mentions]),
                }
            )

    return sort_by_timestamp(rows, "created_at_utc")


def parse_likes(
    archive_dir: Path,
    account: dict[str, Any],
) -> list[dict[str, Any]]:
    source_path = archive_dir / "data" / "like.js"
    source_rows = load_wrapped_js(source_path)
    rows: list[dict[str, Any]] = []
    for index, item in enumerate(source_rows, start=1):
        like = item.get("like", {})
        rows.append(
            {
                "like_record_id": f"{account['account_username']}_like_{index:06d}",
                "account_username": account["account_username"],
                "account_id": account["account_id"],
                "account_email": account["account_email"],
                "account_display_name": account["account_display_name"],
                "source_file": relative_to_project(source_path),
                "tweet_id": like.get("tweetId") or "",
                "full_text": like.get("fullText") or "",
                "expanded_url": like.get("expandedUrl") or "",
                "has_timestamp": False,
            }
        )
    return rows


def parse_messages(
    archive_dir: Path,
    account: dict[str, Any],
) -> list[dict[str, Any]]:
    data_dir = archive_dir / "data"
    rows: list[dict[str, Any]] = []

    for file_name, conversation_type in (
        ("direct-messages.js", "direct"),
        ("direct-messages-group.js", "group"),
    ):
        source_path = data_dir / file_name
        conversations = load_wrapped_js(source_path)
        for conversation in conversations:
            payload = conversation.get("dmConversation", {})
            conversation_id = payload.get("conversationId") or ""
            for index, item in enumerate(payload.get("messages", []), start=1):
                event_name = next(iter(item.keys()))
                event = item[event_name]
                user_ids = event.get("userIds") or event.get("participantsSnapshot") or []
                urls = event.get("urls") or []
                media_urls = event.get("mediaUrls") or []
                rows.append(
                    {
                        "message_record_id": f"{account['account_username']}_message_{len(rows) + 1:06d}",
                        "account_username": account["account_username"],
                        "account_id": account["account_id"],
                        "account_email": account["account_email"],
                        "account_display_name": account["account_display_name"],
                        "source_file": relative_to_project(source_path),
                        "conversation_id": conversation_id,
                        "conversation_type": conversation_type,
                        "event_type": event_name,
                        "event_id": event.get("id") or f"{conversation_id}_{event_name}_{index}",
                        "created_at_utc": format_timestamp(parse_timestamp(event.get("createdAt"))),
                        "sender_id": event.get("senderId") or "",
                        "recipient_id": event.get("recipientId") or "",
                        "initiating_user_id": event.get("initiatingUserId") or "",
                        "text": event.get("text") or "",
                        "url_count": len(urls),
                        "media_url_count": len(media_urls),
                        "reaction_count": len(event.get("reactions") or []),
                        "participant_count": len(user_ids),
                        "participant_user_ids_json": json_text(user_ids),
                        "urls_json": json_text(urls),
                        "media_urls_json": json_text(media_urls),
                    }
                )

    return sort_by_timestamp(rows, "created_at_utc")


def duration_minutes(start_value: str | None, end_value: str | None) -> float | None:
    start = parse_timestamp(start_value)
    end = parse_timestamp(end_value)
    if start is None or end is None:
        return None
    duration = (end - start).total_seconds() / 60
    return round(duration, 4) if duration >= 0 else None


def parse_calls(
    archive_dir: Path,
    account: dict[str, Any],
) -> list[dict[str, Any]]:
    data_dir = archive_dir / "data"
    rows: list[dict[str, Any]] = []

    initiated_path = data_dir / "audio-video-calls-in-dm.js"
    for index, item in enumerate(load_wrapped_js(initiated_path), start=1):
        broadcast = item.get("broadcast", {})
        sessions = item.get("sessions") or []
        rows.append(
            {
                "call_record_id": f"{account['account_username']}_call_{len(rows) + 1:06d}",
                "account_username": account["account_username"],
                "account_id": account["account_id"],
                "account_email": account["account_email"],
                "account_display_name": account["account_display_name"],
                "source_file": relative_to_project(initiated_path),
                "call_kind": "initiated",
                "host_broadcast_id": broadcast.get("id") or f"initiated_{index}",
                "conversation_id": "",
                "created_at_utc": format_timestamp(parse_timestamp(broadcast.get("createdAt"))),
                "started_at_utc": format_timestamp(parse_timestamp(broadcast.get("createdAt"))),
                "published_at_utc": format_timestamp(parse_timestamp(broadcast.get("updatedAt"))),
                "ended_at_utc": format_timestamp(parse_timestamp(broadcast.get("endAt"))),
                "end_reason": "",
                "twitter_user_id": "",
                "invitee_user_ids_json": json_text(broadcast.get("inviteesTwitter") or []),
                "exact_duration_minutes": duration_minutes(broadcast.get("createdAt"), broadcast.get("endAt")),
            }
        )

        for session in sessions:
            rows.append(
                {
                    "call_record_id": f"{account['account_username']}_call_{len(rows) + 1:06d}",
                    "account_username": account["account_username"],
                    "account_id": account["account_id"],
                    "account_email": account["account_email"],
                    "account_display_name": account["account_display_name"],
                    "source_file": relative_to_project(initiated_path),
                    "call_kind": "initiated_session",
                    "host_broadcast_id": session.get("hostBroadcastID") or broadcast.get("id") or "",
                    "conversation_id": "",
                    "created_at_utc": format_timestamp(parse_timestamp(session.get("createdAt"))),
                    "started_at_utc": format_timestamp(parse_timestamp(session.get("startedAt"))),
                    "published_at_utc": format_timestamp(parse_timestamp(session.get("publishedAt"))),
                    "ended_at_utc": format_timestamp(parse_timestamp(session.get("endedAt"))),
                    "end_reason": session.get("endReason") or "",
                    "twitter_user_id": session.get("twitterUserID") or "",
                    "invitee_user_ids_json": json_text([]),
                    "exact_duration_minutes": duration_minutes(session.get("startedAt"), session.get("endedAt")),
                }
            )

    recipient_path = data_dir / "audio-video-calls-in-dm-recipient-sessions.js"
    for index, item in enumerate(load_wrapped_js(recipient_path), start=1):
        rows.append(
            {
                "call_record_id": f"{account['account_username']}_call_{len(rows) + 1:06d}",
                "account_username": account["account_username"],
                "account_id": account["account_id"],
                "account_email": account["account_email"],
                "account_display_name": account["account_display_name"],
                "source_file": relative_to_project(recipient_path),
                "call_kind": "recipient_session",
                "host_broadcast_id": item.get("hostBroadcastID") or f"recipient_{index}",
                "conversation_id": "",
                "created_at_utc": format_timestamp(parse_timestamp(item.get("createdAt"))),
                "started_at_utc": format_timestamp(parse_timestamp(item.get("startedAt"))),
                "published_at_utc": format_timestamp(parse_timestamp(item.get("publishedAt"))),
                "ended_at_utc": format_timestamp(parse_timestamp(item.get("endedAt"))),
                "end_reason": item.get("endReason") or "",
                "twitter_user_id": item.get("twitterUserID") or "",
                "invitee_user_ids_json": json_text([]),
                "exact_duration_minutes": duration_minutes(item.get("startedAt"), item.get("endedAt")),
            }
        )

    return sort_by_timestamp(rows, "started_at_utc")


def parse_spaces(
    archive_dir: Path,
    account: dict[str, Any],
) -> list[dict[str, Any]]:
    source_path = archive_dir / "data" / "spaces-metadata.js"
    rows: list[dict[str, Any]] = []
    for index, item in enumerate(load_wrapped_js(source_path), start=1):
        speakers = item.get("speakers") or []
        rows.append(
            {
                "space_record_id": f"{account['account_username']}_space_{index:06d}",
                "account_username": account["account_username"],
                "account_id": account["account_id"],
                "account_email": account["account_email"],
                "account_display_name": account["account_display_name"],
                "source_file": relative_to_project(source_path),
                "space_id": item.get("id") or "",
                "creator_user_id": item.get("creatorUserId") or "",
                "created_at_utc": format_timestamp(parse_timestamp(item.get("createdAt"))),
                "ended_at_utc": format_timestamp(parse_timestamp(item.get("endedAt"))),
                "exact_duration_minutes": duration_minutes(item.get("createdAt"), item.get("endedAt")),
                "total_participating": normalize_int(item.get("totalParticipating")),
                "total_participated": normalize_int(item.get("totalParticipated")),
                "speaker_count": len(speakers),
            }
        )
    return sort_by_timestamp(rows, "created_at_utc")


def build_activity_events(
    tweets: list[dict[str, Any]],
    messages: list[dict[str, Any]],
    calls: list[dict[str, Any]],
    spaces: list[dict[str, Any]],
    account: dict[str, Any],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []

    for tweet in tweets:
        rows.append(
            {
                "activity_id": "",
                "account_username": account["account_username"],
                "account_id": account["account_id"],
                "account_email": account["account_email"],
                "account_display_name": account["account_display_name"],
                "source_dataset": "tweets",
                "source_file": tweet["source_file"],
                "event_type": tweet["tweet_type"],
                "timestamp_utc": tweet["created_at_utc"],
                "primary_id": tweet["tweet_id"],
                "conversation_id": "",
                "text": tweet["full_text"],
                "source_app": tweet["source_app"],
                "url_count": tweet["url_count"],
                "media_count": 0,
                "exact_duration_minutes": None,
                "is_deleted_tweet": tweet["is_deleted"],
            }
        )

    for message in messages:
        rows.append(
            {
                "activity_id": "",
                "account_username": account["account_username"],
                "account_id": account["account_id"],
                "account_email": account["account_email"],
                "account_display_name": account["account_display_name"],
                "source_dataset": "messages",
                "source_file": message["source_file"],
                "event_type": message["event_type"],
                "timestamp_utc": message["created_at_utc"],
                "primary_id": message["event_id"],
                "conversation_id": message["conversation_id"],
                "text": message["text"],
                "source_app": "",
                "url_count": message["url_count"],
                "media_count": message["media_url_count"],
                "exact_duration_minutes": None,
                "is_deleted_tweet": False,
            }
        )

    for call in calls:
        timestamp = call["started_at_utc"] or call["created_at_utc"]
        rows.append(
            {
                "activity_id": "",
                "account_username": account["account_username"],
                "account_id": account["account_id"],
                "account_email": account["account_email"],
                "account_display_name": account["account_display_name"],
                "source_dataset": "calls",
                "source_file": call["source_file"],
                "event_type": call["call_kind"],
                "timestamp_utc": timestamp,
                "primary_id": call["call_record_id"],
                "conversation_id": call["conversation_id"],
                "text": "",
                "source_app": "",
                "url_count": 0,
                "media_count": 0,
                "exact_duration_minutes": call["exact_duration_minutes"],
                "is_deleted_tweet": False,
            }
        )

    for space in spaces:
        rows.append(
            {
                "activity_id": "",
                "account_username": account["account_username"],
                "account_id": account["account_id"],
                "account_email": account["account_email"],
                "account_display_name": account["account_display_name"],
                "source_dataset": "spaces",
                "source_file": space["source_file"],
                "event_type": "space",
                "timestamp_utc": space["created_at_utc"],
                "primary_id": space["space_id"] or space["space_record_id"],
                "conversation_id": "",
                "text": "",
                "source_app": "",
                "url_count": 0,
                "media_count": 0,
                "exact_duration_minutes": space["exact_duration_minutes"],
                "is_deleted_tweet": False,
            }
        )

    rows = sort_by_timestamp(rows, "timestamp_utc")
    for index, row in enumerate(rows, start=1):
        row["activity_id"] = f"{account['account_username']}_activity_{index:06d}"
    return rows


def summarize_account(
    account: dict[str, Any],
    tweets: list[dict[str, Any]],
    likes: list[dict[str, Any]],
    messages: list[dict[str, Any]],
    calls: list[dict[str, Any]],
    spaces: list[dict[str, Any]],
    events: list[dict[str, Any]],
    follower_count: int,
    following_count: int,
    event_chunk_count: int,
) -> dict[str, Any]:
    timestamps = [row["timestamp_utc"] for row in events if row.get("timestamp_utc")]
    exact_duration_total = sum(float(row.get("exact_duration_minutes") or 0) for row in calls + spaces)
    return {
        "account_username": account["account_username"],
        "account_id": account["account_id"],
        "account_email": account["account_email"],
        "account_display_name": account["account_display_name"],
        "account_created_at_utc": account["account_created_at_utc"],
        "tweet_count": len(tweets),
        "deleted_tweet_count": sum(1 for row in tweets if row["is_deleted"]),
        "like_count": len(likes),
        "message_event_count": len(messages),
        "direct_message_count": sum(1 for row in messages if row["conversation_type"] == "direct" and row["event_type"] == "messageCreate"),
        "group_message_count": sum(1 for row in messages if row["conversation_type"] == "group" and row["event_type"] == "messageCreate"),
        "activity_event_count": len(events),
        "call_count": len(calls),
        "space_count": len(spaces),
        "exact_duration_minutes": round(exact_duration_total, 4),
        "follower_count": follower_count,
        "following_count": following_count,
        "event_chunk_count": event_chunk_count,
        "activity_start_utc": min(timestamps) if timestamps else None,
        "activity_end_utc": max(timestamps) if timestamps else None,
    }


def assign_prefix_ids(rows: list[dict[str, Any]], field_name: str, prefix: str) -> list[dict[str, Any]]:
    assigned: list[dict[str, Any]] = []
    for index, row in enumerate(rows, start=1):
        enriched = dict(row)
        enriched[field_name] = f"{prefix}_{index:06d}"
        assigned.append(enriched)
    return assigned


def write_account_outputs(
    output_root: Path,
    account: dict[str, Any],
    tweets: list[dict[str, Any]],
    likes: list[dict[str, Any]],
    messages: list[dict[str, Any]],
    calls: list[dict[str, Any]],
    spaces: list[dict[str, Any]],
    events: list[dict[str, Any]],
    *,
    lines_per_chunk: int,
) -> int:
    account_dir = output_root / "accounts" / account["account_username"]
    account_dir.mkdir(parents=True, exist_ok=True)

    (account_dir / "account_metadata.json").write_text(
        json.dumps(account, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    write_csv(tweets, TWEET_FIELDS, account_dir / "twitter_tweets.csv")
    write_csv(likes, LIKE_FIELDS, account_dir / "twitter_likes.csv")
    write_csv(messages, MESSAGE_FIELDS, account_dir / "twitter_messages.csv")
    write_csv(calls, CALL_FIELDS, account_dir / "twitter_calls.csv")
    write_csv(spaces, SPACE_FIELDS, account_dir / "twitter_spaces.csv")
    write_csv(events, EVENT_FIELDS, account_dir / "twitter_activity_events.csv")
    write_jsonl(events, account_dir / "twitter_activity_events.jsonl")
    return write_jsonl_chunks(
        events,
        account_dir / "chunks",
        prefix=f"{account['account_username']}_twitter_activity",
        lines_per_file=lines_per_chunk,
    )


def write_combined_outputs(
    output_root: Path,
    tweets: list[dict[str, Any]],
    likes: list[dict[str, Any]],
    messages: list[dict[str, Any]],
    calls: list[dict[str, Any]],
    spaces: list[dict[str, Any]],
    events: list[dict[str, Any]],
    *,
    lines_per_chunk: int,
) -> int:
    combined_dir = output_root / "combined"
    combined_dir.mkdir(parents=True, exist_ok=True)

    write_csv(tweets, TWEET_FIELDS, combined_dir / "twitter_tweets_merged.csv")
    write_csv(likes, LIKE_FIELDS, combined_dir / "twitter_likes_merged.csv")
    write_csv(messages, MESSAGE_FIELDS, combined_dir / "twitter_messages_merged.csv")
    write_csv(calls, CALL_FIELDS, combined_dir / "twitter_calls_merged.csv")
    write_csv(spaces, SPACE_FIELDS, combined_dir / "twitter_spaces_merged.csv")
    write_csv(events, EVENT_FIELDS, combined_dir / "twitter_activity_events_merged.csv")
    write_jsonl(events, combined_dir / "twitter_activity_events_merged.jsonl")
    return write_jsonl_chunks(
        events,
        combined_dir / "chunks",
        prefix="twitter_activity_merged",
        lines_per_file=lines_per_chunk,
    )


def main() -> None:
    args = parse_args()
    raw_dir = Path(args.raw_dir).resolve()
    output_dir = Path(args.output_dir).resolve()
    archives = discover_archives(raw_dir)
    if not archives:
        raise FileNotFoundError(f"No Twitter archives with data/account.js found in {raw_dir}")

    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    combined_tweets: list[dict[str, Any]] = []
    combined_likes: list[dict[str, Any]] = []
    combined_messages: list[dict[str, Any]] = []
    combined_calls: list[dict[str, Any]] = []
    combined_spaces: list[dict[str, Any]] = []
    combined_events: list[dict[str, Any]] = []
    account_summaries: list[dict[str, Any]] = []

    for archive_dir in archives:
        data_dir = archive_dir / "data"
        account = parse_account_metadata(data_dir)
        tweets = assign_prefix_ids(
            parse_tweets(archive_dir, account),
            "tweet_record_id",
            f"{account['account_username']}_tweet",
        )
        likes = assign_prefix_ids(
            parse_likes(archive_dir, account),
            "like_record_id",
            f"{account['account_username']}_like",
        )
        messages = assign_prefix_ids(
            parse_messages(archive_dir, account),
            "message_record_id",
            f"{account['account_username']}_message",
        )
        calls = assign_prefix_ids(
            parse_calls(archive_dir, account),
            "call_record_id",
            f"{account['account_username']}_call",
        )
        spaces = assign_prefix_ids(
            parse_spaces(archive_dir, account),
            "space_record_id",
            f"{account['account_username']}_space",
        )
        events = build_activity_events(tweets, messages, calls, spaces, account)

        follower_count = len(load_wrapped_js(data_dir / "follower.js"))
        following_count = len(load_wrapped_js(data_dir / "following.js"))
        event_chunk_count = write_account_outputs(
            output_dir,
            account,
            tweets,
            likes,
            messages,
            calls,
            spaces,
            events,
            lines_per_chunk=args.lines_per_chunk,
        )
        account_summaries.append(
            summarize_account(
                account,
                tweets,
                likes,
                messages,
                calls,
                spaces,
                events,
                follower_count,
                following_count,
                event_chunk_count,
            )
        )

        combined_tweets.extend(tweets)
        combined_likes.extend(likes)
        combined_messages.extend(messages)
        combined_calls.extend(calls)
        combined_spaces.extend(spaces)
        combined_events.extend(events)

    combined_tweets = sort_by_timestamp(combined_tweets, "created_at_utc")
    combined_messages = sort_by_timestamp(combined_messages, "created_at_utc")
    combined_calls = sort_by_timestamp(combined_calls, "started_at_utc")
    combined_spaces = sort_by_timestamp(combined_spaces, "created_at_utc")
    combined_events = sort_by_timestamp(combined_events, "timestamp_utc")

    combined_event_chunk_count = write_combined_outputs(
        output_dir,
        combined_tweets,
        combined_likes,
        combined_messages,
        combined_calls,
        combined_spaces,
        combined_events,
        lines_per_chunk=args.lines_per_chunk,
    )

    combined_timestamps = [row["timestamp_utc"] for row in combined_events if row.get("timestamp_utc")]
    build_summary = {
        "raw_dir": relative_to_project(raw_dir),
        "output_dir": relative_to_project(output_dir),
        "archive_count": len(archives),
        "accounts": account_summaries,
        "combined": {
            "tweet_count": len(combined_tweets),
            "like_count": len(combined_likes),
            "message_event_count": len(combined_messages),
            "call_count": len(combined_calls),
            "space_count": len(combined_spaces),
            "activity_event_count": len(combined_events),
            "activity_start_utc": min(combined_timestamps) if combined_timestamps else None,
            "activity_end_utc": max(combined_timestamps) if combined_timestamps else None,
            "exact_duration_minutes": round(
                sum(float(row.get("exact_duration_minutes") or 0) for row in combined_calls + combined_spaces),
                4,
            ),
            "event_chunk_count": combined_event_chunk_count,
            "tweets_csv_path": "data/processed/twitter/combined/twitter_tweets_merged.csv",
            "likes_csv_path": "data/processed/twitter/combined/twitter_likes_merged.csv",
            "messages_csv_path": "data/processed/twitter/combined/twitter_messages_merged.csv",
            "events_csv_path": "data/processed/twitter/combined/twitter_activity_events_merged.csv",
        },
    }

    summary_path = output_dir / "build_summary.json"
    summary_path.write_text(json.dumps(build_summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(build_summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
