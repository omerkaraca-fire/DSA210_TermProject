#!/usr/bin/env python3
"""Parse a pasted Prime Video watch-history text export into structured datasets."""

from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_RAW_PATH = REPO_ROOT / "data_local" / "raw" / "prime_video" / "raw.txt"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "data_local" / "processed" / "prime_video"

PAGE_BREAK_RE = re.compile(r"^\d+ / \d+ \d{2}\.\d{2}\.\d{4} \d{2}:\d{2}$")
DATE_RE = re.compile(r"^(\d{1,2})\s+([A-ZÇĞİÖŞÜa-zçğıöşü]+)\s+(\d{4})\s+[A-ZÇĞİÖŞÜa-zçğıöşü]+$")
EPISODE_RE = re.compile(r"^(\d+)\.\s*Bölüm:\s*(.*)$")

MONTHS_TR = {
    "Ocak": 1,
    "Şubat": 2,
    "Mart": 3,
    "Nisan": 4,
    "Mayıs": 5,
    "Haziran": 6,
    "Temmuz": 7,
    "Ağustos": 8,
    "Eylül": 9,
    "Ekim": 10,
    "Kasım": 11,
    "Aralık": 12,
}

NUMBER_WORDS = {
    "first": 1,
    "birinci": 1,
    "second": 2,
    "ikinci": 2,
    "third": 3,
    "üçüncü": 3,
    "fourth": 4,
    "dördüncü": 4,
    "fifth": 5,
    "beşinci": 5,
    "sixth": 6,
    "altıncı": 6,
    "seventh": 7,
    "yedinci": 7,
    "eighth": 8,
    "sekizinci": 8,
    "ninth": 9,
    "dokuzuncu": 9,
    "tenth": 10,
    "onuncu": 10,
    "eleventh": 11,
    "on birinci": 11,
    "twelveth": 12,
    "twelfth": 12,
    "on ikinci": 12,
    "thirteenth": 13,
    "on üçüncü": 13,
}

IGNORE_PREFIXES = (
    "Prime Video: Hesap ve Ayarlar",
    "https://www.primevideo.com/",
    "Koşullar ve Gizlilik Bildirimi",
    "© 1996-2026",
)

RECORD_FIELDS = [
    "record_id",
    "watch_date",
    "date_assignment_method",
    "source_page",
    "record_type",
    "title",
    "series_title",
    "season_label",
    "season_number",
    "episode_number",
    "episode_title",
    "movie_title",
    "raw_title",
    "title_missing",
]

ISSUE_FIELDS = [
    "issue_id",
    "issue_type",
    "source_page",
    "watch_date_guess",
    "title_guess",
    "context",
]

DAY_SUMMARY_FIELDS = [
    "watch_date",
    "record_count",
    "episode_count",
    "movie_count",
    "unique_titles",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a structured Prime Video dataset from raw pasted text.")
    parser.add_argument(
        "--raw-path",
        default=str(DEFAULT_RAW_PATH),
        help="Path to the pasted Prime Video raw text file.",
    )
    parser.add_argument(
        "--output-dir",
        default=str(DEFAULT_OUTPUT_DIR),
        help="Directory where processed Prime Video outputs will be written.",
    )
    return parser.parse_args()


def normalize_space(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip(" -:–")


def is_date_line(line: str) -> bool:
    return bool(DATE_RE.match(line))


def parse_date_line(line: str) -> str:
    match = DATE_RE.match(line)
    if match is None:
        raise ValueError(f"Not a Prime Video date line: {line}")
    day_text, month_text, year_text = match.groups()
    return f"{int(year_text):04d}-{MONTHS_TR[month_text]:02d}-{int(day_text):02d}"


def split_into_pages(lines: list[str]) -> list[list[str]]:
    pages: list[list[str]] = []
    current: list[str] = []
    for line in lines:
        if PAGE_BREAK_RE.match(line.strip()):
            pages.append(current)
            current = []
        else:
            current.append(line.rstrip())
    pages.append(current)
    return pages


def clean_page(lines: list[str]) -> list[str]:
    cleaned: list[str] = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if PAGE_BREAK_RE.match(line):
            continue
        if any(line.startswith(prefix) for prefix in IGNORE_PREFIXES):
            continue
        cleaned.append(line)
    return cleaned


def looks_like_title_block(lines: list[str], start_index: int) -> bool:
    for index in range(start_index, min(len(lines), start_index + 8)):
        line = lines[index]
        if is_date_line(line) or EPISODE_RE.match(line):
            return False
        if "Filmi İzleme Geçmişinden sil" in line or "İzleme Geçmişi" in line or "İzlenen bölümler" in line:
            return True
    return False


def extract_series_metadata(raw_title: str) -> tuple[str, str | None, int | None]:
    title = normalize_space(raw_title)
    season_label = None
    season_number = None

    digit_patterns = [
        re.compile(r"^(?P<title>.*?)(?:\s*[-:]\s*|\s+)(?P<label>(?:Season|Sezon)\s*(?P<number>\d+))$", re.IGNORECASE),
        re.compile(r"^(?P<title>.*?)(?:\s*[-:]\s*|\s+)(?P<label>(?P<number>\d+)\.?\s*(?:Season|Sezon))$", re.IGNORECASE),
    ]
    for pattern in digit_patterns:
        match = pattern.match(title)
        if match:
            season_label = normalize_space(match.group("label"))
            season_number = int(match.group("number"))
            title = normalize_space(match.group("title"))
            return title, season_label, season_number

    word_pattern = re.compile(
        r"^(?P<title>.*?)(?:\s*[-:]\s*|\s+)(?P<label>(?:The Complete|Complete)?\s*(?P<word>[A-Za-zÇĞİÖŞÜa-zçğıöşü\s]+)\s+Season)$",
        re.IGNORECASE,
    )
    match = word_pattern.match(title)
    if match:
        candidate = normalize_space(match.group("word")).lower()
        if candidate in NUMBER_WORDS:
            season_label = normalize_space(match.group("label"))
            season_number = NUMBER_WORDS[candidate]
            title = normalize_space(match.group("title"))
            return title, season_label, season_number

    return title, season_label, season_number


def is_suspicious_series_title(record: dict[str, Any]) -> bool:
    title = (record.get("series_title") or "").strip()
    raw_title = (record.get("raw_title") or "").strip()
    if not title:
        return True
    if title in {"The", "Mark", "Girl", "Men", "Season", "Sezon"}:
        return True
    if title.endswith("–"):
        return True
    if title == "The" and raw_title.lower().startswith("the complete "):
        return True
    return False


def postprocess_records(records: list[dict[str, Any]], issues: list[dict[str, Any]]) -> None:
    contaminated_episode_tail = re.compile(
        r"^(?P<episode>.+?)\s+(?P<series>[A-ZÇĞİÖŞÜA-Za-z0-9].*(?:Season|Sezon).*)$",
        re.IGNORECASE,
    )
    episode_prefix = re.compile(r"^\d+\.\s*Bölüm:\s*")

    for record in records:
        if record["record_type"] != "episode":
            continue

        episode_title = normalize_space(record.get("episode_title") or "")
        episode_title = normalize_space(episode_prefix.sub("", episode_title))

        if "İzleme Geçmişi" in episode_title:
            prefix = normalize_space(episode_title.split("İzleme Geçmişi", 1)[0])
            match = contaminated_episode_tail.match(prefix)
            if match:
                episode_title = normalize_space(match.group("episode"))
                candidate_raw_title = normalize_space(match.group("series"))
                if is_suspicious_series_title(record):
                    series_title, season_label, season_number = extract_series_metadata(candidate_raw_title)
                    record["title"] = series_title or candidate_raw_title
                    record["series_title"] = series_title or candidate_raw_title
                    record["season_label"] = season_label or ""
                    record["season_number"] = season_number
                    record["raw_title"] = candidate_raw_title
                    record["title_missing"] = False
            else:
                episode_title = prefix

        record["episode_title"] = episode_title

    grouped: dict[tuple[int, str], list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        if record["record_type"] == "episode":
            grouped[(int(record["source_page"]), str(record["watch_date"]))].append(record)

    for group_records in grouped.values():
        valid_titles = {
            (record.get("series_title") or "").strip()
            for record in group_records
            if not is_suspicious_series_title(record)
        }
        if len(valid_titles) != 1:
            continue
        series_title = next(iter(valid_titles))
        exemplar = next(
            record for record in group_records if (record.get("series_title") or "").strip() == series_title
        )
        for record in group_records:
            if is_suspicious_series_title(record):
                record["title"] = exemplar["title"]
                record["series_title"] = exemplar["series_title"]
                record["season_label"] = exemplar["season_label"]
                record["season_number"] = exemplar["season_number"]
                record["raw_title"] = exemplar["raw_title"]
                record["title_missing"] = False

    previous_episode: dict[str, Any] | None = None
    for record in records:
        if record["record_type"] != "episode":
            continue
        if is_suspicious_series_title(record):
            if (
                previous_episode
                and not is_suspicious_series_title(previous_episode)
                and int(record["source_page"]) - int(previous_episode["source_page"]) <= 1
            ):
                record["title"] = previous_episode["title"]
                record["series_title"] = previous_episode["series_title"]
                if not record["season_label"]:
                    record["season_label"] = previous_episode["season_label"]
                    record["season_number"] = previous_episode["season_number"]
                if not record["raw_title"]:
                    record["raw_title"] = previous_episode["raw_title"]
                record["title_missing"] = False
        previous_episode = record

    for record in records:
        if record["record_type"] == "episode" and is_suspicious_series_title(record):
            issues.append(
                {
                    "issue_id": "",
                    "issue_type": "episode_suspicious_series_title",
                    "source_page": record["source_page"],
                    "watch_date_guess": record["watch_date"],
                    "title_guess": record.get("series_title") or "",
                    "context": record.get("episode_title") or "",
                }
            )


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


def repo_relative_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def parse_prime_video(raw_path: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[list[str]]]:
    raw_lines = raw_path.read_text(encoding="utf-8").splitlines()
    pages = split_into_pages(raw_lines)
    cleaned_pages = [clean_page(page) for page in pages]
    if cleaned_pages and not cleaned_pages[-1]:
        cleaned_pages = cleaned_pages[:-1]

    records: list[dict[str, Any]] = []
    issues: list[dict[str, Any]] = []

    pending_dates: list[str] = []
    current_date: str | None = None
    current_series_title: str | None = None
    current_series_raw_title: str | None = None
    current_series_has_records = False
    current_block_active = False
    current_date_method = "carryover"

    def begin_block() -> str:
        nonlocal current_date, current_block_active, current_date_method
        method = "carryover"
        if pending_dates:
            current_date = pending_dates.pop(0)
            method = "queued_page_date"
        current_block_active = True
        current_date_method = method
        return method

    def flush_series_without_records(page_number: int) -> None:
        nonlocal current_series_title, current_series_raw_title, current_series_has_records
        if current_series_title and not current_series_has_records:
            issues.append(
                {
                    "issue_id": "",
                    "issue_type": "series_block_without_items",
                    "source_page": page_number,
                    "watch_date_guess": current_date,
                    "title_guess": current_series_title,
                    "context": current_series_raw_title or current_series_title,
                }
            )
            current_series_title = None
            current_series_raw_title = None
        current_series_has_records = False

    for page_number, page_lines in enumerate(cleaned_pages, start=1):
        index = 0
        title_buffer: list[str] = []

        while index < len(page_lines):
            line = page_lines[index]

            if is_date_line(line):
                flush_series_without_records(page_number)
                pending_dates.append(parse_date_line(line))
                current_block_active = False
                title_buffer = []
                index += 1
                continue

            if "Filmi İzleme Geçmişinden sil" in line:
                prefix = normalize_space(line.split("Filmi İzleme Geçmişinden sil", 1)[0])
                movie_title = normalize_space(" ".join(title_buffer + ([prefix] if prefix else [])))
                date_method = begin_block()
                records.append(
                    {
                        "record_id": "",
                        "watch_date": current_date,
                        "date_assignment_method": date_method,
                        "source_page": page_number,
                        "record_type": "movie",
                        "title": movie_title,
                        "series_title": "",
                        "season_label": "",
                        "season_number": None,
                        "episode_number": None,
                        "episode_title": "",
                        "movie_title": movie_title,
                        "raw_title": movie_title,
                        "title_missing": not bool(movie_title),
                    }
                )
                if not movie_title:
                    issues.append(
                        {
                            "issue_id": "",
                            "issue_type": "blank_movie_title",
                            "source_page": page_number,
                            "watch_date_guess": current_date,
                            "title_guess": "",
                            "context": " ".join(title_buffer),
                        }
                    )
                title_buffer = []
                current_series_title = None
                current_series_raw_title = None
                current_series_has_records = False
                index += 1
                continue

            if "İzlenen bölümler" in line or "İzleme Geçmişi'nden bölümleri sil" in line:
                marker = "İzlenen bölümler" if "İzlenen bölümler" in line else "İzleme Geçmişi'nden bölümleri sil"
                prefix = normalize_space(line.split(marker, 1)[0])
                raw_title = normalize_space(" ".join(title_buffer + ([prefix] if prefix else [])))
                if raw_title or current_series_title is None:
                    flush_series_without_records(page_number)
                    begin_block()
                    current_series_raw_title = raw_title or current_series_raw_title
                    current_series_title = raw_title or current_series_title
                    current_series_has_records = False
                title_buffer = []
                index += 1
                continue

            episode_match = EPISODE_RE.match(line)
            if episode_match:
                if not current_block_active:
                    begin_block()

                episode_number = int(episode_match.group(1))
                episode_title = episode_match.group(2).strip()
                lookahead = index + 1
                while lookahead < len(page_lines):
                    next_line = page_lines[lookahead]
                    if is_date_line(next_line) or EPISODE_RE.match(next_line) or "Filmi İzleme Geçmişinden sil" in next_line:
                        break
                    if looks_like_title_block(page_lines, lookahead):
                        if lookahead + 1 < len(page_lines) and looks_like_title_block(page_lines, lookahead + 1):
                            episode_title += " " + next_line.strip()
                            lookahead += 1
                            continue
                        break
                    episode_title += " " + next_line.strip()
                    lookahead += 1

                episode_title = normalize_space(episode_title)
                series_title = current_series_title or ""
                raw_title = current_series_raw_title or series_title
                normalized_series_title, season_label, season_number = extract_series_metadata(series_title)

                records.append(
                    {
                        "record_id": "",
                        "watch_date": current_date,
                        "date_assignment_method": current_date_method,
                        "source_page": page_number,
                        "record_type": "episode",
                        "title": normalized_series_title or series_title,
                        "series_title": normalized_series_title or series_title,
                        "season_label": season_label or "",
                        "season_number": season_number,
                        "episode_number": episode_number,
                        "episode_title": episode_title,
                        "movie_title": "",
                        "raw_title": raw_title,
                        "title_missing": not bool(series_title),
                    }
                )
                if not series_title:
                    issues.append(
                        {
                            "issue_id": "",
                            "issue_type": "episode_missing_series_title",
                            "source_page": page_number,
                            "watch_date_guess": current_date,
                            "title_guess": "",
                            "context": f"{episode_number}. Bölüm: {episode_title}",
                        }
                    )

                current_series_has_records = True
                current_block_active = True
                index = lookahead
                continue

            title_buffer.append(line)
            index += 1

    flush_series_without_records(len(cleaned_pages))

    for index, record in enumerate(records, start=1):
        record["record_id"] = f"prime_video_{index:06d}"

    for index, issue in enumerate(issues, start=1):
        issue["issue_id"] = f"prime_video_issue_{index:06d}"

    return records, issues, cleaned_pages


def build_day_summary(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        grouped[record["watch_date"]].append(record)

    summary_rows: list[dict[str, Any]] = []
    for watch_date in sorted(grouped):
        day_rows = grouped[watch_date]
        summary_rows.append(
            {
                "watch_date": watch_date,
                "record_count": len(day_rows),
                "episode_count": sum(1 for row in day_rows if row["record_type"] == "episode"),
                "movie_count": sum(1 for row in day_rows if row["record_type"] == "movie"),
                "unique_titles": len({row["title"] for row in day_rows if row["title"]}),
            }
        )
    return summary_rows


def build_outputs(*, raw_path: Path, output_dir: Path) -> dict[str, Any]:
    raw_path = raw_path.resolve()
    output_dir = output_dir.resolve()
    if not raw_path.is_file():
        raise FileNotFoundError(f"Prime Video raw text file not found: {raw_path}")

    output_dir.mkdir(parents=True, exist_ok=True)

    records, issues, cleaned_pages = parse_prime_video(raw_path)
    postprocess_records(records, issues)

    # Postprocessing can append more issues, so assign IDs after all parser passes.
    for index, issue in enumerate(issues, start=1):
        issue["issue_id"] = f"prime_video_issue_{index:06d}"

    day_summary = build_day_summary(records)

    write_csv(records, RECORD_FIELDS, output_dir / "prime_video_watch_history.csv")
    write_jsonl(records, output_dir / "prime_video_watch_history.jsonl")
    write_csv(day_summary, DAY_SUMMARY_FIELDS, output_dir / "prime_video_day_summary.csv")
    write_csv(issues, ISSUE_FIELDS, output_dir / "prime_video_parse_issues.csv")
    (output_dir / "cleaned_pages.json").write_text(
        json.dumps(cleaned_pages, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    title_counter = Counter(record["title"] for record in records if record["title"])
    build_summary = {
        "dataset": "prime_video_watch_history_processed",
        "raw_path": repo_relative_path(raw_path),
        "output_dir": repo_relative_path(output_dir),
        "record_count": len(records),
        "episode_count": sum(1 for record in records if record["record_type"] == "episode"),
        "movie_count": sum(1 for record in records if record["record_type"] == "movie"),
        "records_with_missing_title": sum(1 for record in records if record["title_missing"]),
        "issue_count": len(issues),
        "day_count": len(day_summary),
        "watch_start_date": min((record["watch_date"] for record in records), default=None),
        "watch_end_date": max((record["watch_date"] for record in records), default=None),
        "unique_titles": len(title_counter),
        "top_titles": title_counter.most_common(10),
        "files": {
            "watch_history_csv": "prime_video_watch_history.csv",
            "watch_history_jsonl": "prime_video_watch_history.jsonl",
            "day_summary_csv": "prime_video_day_summary.csv",
            "parse_issues_csv": "prime_video_parse_issues.csv",
            "cleaned_pages_json": "cleaned_pages.json",
            "summary": "build_summary.json",
        },
        "schema": RECORD_FIELDS,
    }
    (output_dir / "build_summary.json").write_text(
        json.dumps(build_summary, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return {
        "raw_path": str(raw_path),
        "output_dir": str(output_dir),
        "record_count": build_summary["record_count"],
        "episode_count": build_summary["episode_count"],
        "movie_count": build_summary["movie_count"],
        "records_with_missing_title": build_summary["records_with_missing_title"],
        "issue_count": build_summary["issue_count"],
        "day_count": build_summary["day_count"],
        "date_range": {
            "min": build_summary["watch_start_date"],
            "max": build_summary["watch_end_date"],
        },
        "unique_titles": build_summary["unique_titles"],
        "outputs": {
            "watch_history_csv": str(output_dir / "prime_video_watch_history.csv"),
            "watch_history_jsonl": str(output_dir / "prime_video_watch_history.jsonl"),
            "day_summary_csv": str(output_dir / "prime_video_day_summary.csv"),
            "parse_issues_csv": str(output_dir / "prime_video_parse_issues.csv"),
            "summary": str(output_dir / "build_summary.json"),
        },
    }


def main() -> None:
    args = parse_args()
    summary = build_outputs(
        raw_path=Path(args.raw_path),
        output_dir=Path(args.output_dir),
    )
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
