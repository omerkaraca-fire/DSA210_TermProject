#!/usr/bin/env python3
"""Convert a Google My Activity HTML export into CSV and JSONL files."""

from __future__ import annotations

import argparse
import csv
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

from bs4 import BeautifulSoup, NavigableString, Tag


REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_INPUT = REPO_ROOT / "data_local" / "raw" / "youtube_legacy" / "MyActivity.html"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "data_local" / "processed" / "youtube_legacy"
OUTER_CELL_SPLIT = '<div class="outer-cell '
TIMESTAMP_RE = re.compile(r"^[A-Z][a-z]{2} \d{1,2}, \d{4}, .+ GMT[+-]\d{2}:\d{2}$")


def normalize_whitespace(value: str) -> str:
    replacements = {
        "\u00a0": " ",
        "\u202f": " ",
        "\u2009": " ",
        "\u200a": " ",
        "\u200b": "",
        "\ufeff": "",
    }
    for old, new in replacements.items():
        value = value.replace(old, new)
    return re.sub(r"[ \t\r\f\v]+", " ", value).strip()


def parse_timestamp(timestamp_text: str | None) -> str | None:
    if not timestamp_text:
        return None

    normalized = normalize_whitespace(timestamp_text)
    normalized = normalized.replace("GMT", "")
    normalized = re.sub(r"([+-]\d{2}):(\d{2})$", r"\1\2", normalized)
    try:
        parsed = datetime.strptime(normalized, "%b %d, %Y, %I:%M:%S %p %z")
    except ValueError:
        return None
    return parsed.isoformat()


def tag_text(tag: Tag | None) -> str:
    if tag is None:
        return ""
    return normalize_whitespace(tag.get_text("\n", strip=True))


def extract_links(tag: Tag | None) -> list[dict[str, str]]:
    if tag is None:
        return []

    links: list[dict[str, str]] = []
    for index, anchor in enumerate(tag.find_all("a"), start=1):
        links.append(
            {
                "position": index,
                "text": normalize_whitespace(anchor.get_text(" ", strip=True)),
                "href": anchor.get("href", "").strip(),
            }
        )
    return links


def parse_caption_sections(caption_cell: Tag | None) -> dict[str, str]:
    if caption_cell is None:
        return {}

    sections: dict[str, list[str]] = {}
    current_key: str | None = None

    for node in caption_cell.children:
        if isinstance(node, Tag) and node.name == "b":
            current_key = normalize_whitespace(node.get_text(" ", strip=True)).rstrip(":")
            sections.setdefault(current_key, [])
            continue

        if current_key is None:
            continue

        if isinstance(node, NavigableString):
            text = normalize_whitespace(str(node))
            if text:
                sections[current_key].append(text)
            continue

        if isinstance(node, Tag):
            text = normalize_whitespace(node.get_text(" ", strip=True))
            if text:
                sections[current_key].append(text)

    return {key: normalize_whitespace(" ".join(values)) for key, values in sections.items()}


def parse_body_cell(body_cell: Tag | None) -> dict[str, Any]:
    lines = [normalize_whitespace(text) for text in body_cell.stripped_strings] if body_cell else []
    links = extract_links(body_cell)

    timestamp_text = lines[-1] if lines and TIMESTAMP_RE.match(lines[-1]) else None
    body_without_timestamp = lines[:-1] if timestamp_text else lines
    action = body_without_timestamp[0] if body_without_timestamp else ""
    detail_lines = body_without_timestamp[1:] if len(body_without_timestamp) > 1 else []

    primary_link = links[0] if links else {"text": "", "href": ""}
    secondary_link = links[1] if len(links) > 1 else {"text": "", "href": ""}

    return {
        "action": action,
        "timestamp_text": timestamp_text,
        "timestamp_iso": parse_timestamp(timestamp_text),
        "detail_lines": detail_lines,
        "detail_text": " | ".join(detail_lines),
        "body_lines": lines,
        "body_text": " | ".join(lines),
        "links": links,
        "link_count": len(links),
        "primary_text": primary_link["text"],
        "primary_url": primary_link["href"],
        "secondary_text": secondary_link["text"],
        "secondary_url": secondary_link["href"],
    }


def parse_entry(index: int, fragment: str) -> dict[str, Any]:
    soup = BeautifulSoup(fragment, "html.parser")

    header = tag_text(soup.select_one("div.header-cell p"))
    content_cells = soup.select("div.content-cell")
    left_cell = content_cells[0] if len(content_cells) > 0 else None
    right_cell = content_cells[1] if len(content_cells) > 1 else None
    caption_cell = content_cells[-1] if content_cells else None

    body = parse_body_cell(left_cell)
    caption_sections = parse_caption_sections(caption_cell)

    content_cells_data = []
    for position, cell in enumerate(content_cells, start=1):
        content_cells_data.append(
            {
                "position": position,
                "classes": cell.get("class", []),
                "text": tag_text(cell),
                "links": extract_links(cell),
            }
        )

    return {
        "activity_id": index,
        "service": header,
        "action": body["action"],
        "timestamp_text": body["timestamp_text"],
        "timestamp_iso": body["timestamp_iso"],
        "detail_text": body["detail_text"],
        "detail_lines": body["detail_lines"],
        "primary_text": body["primary_text"],
        "primary_url": body["primary_url"],
        "secondary_text": body["secondary_text"],
        "secondary_url": body["secondary_url"],
        "body_text": body["body_text"],
        "body_lines": body["body_lines"],
        "body_links": body["links"],
        "body_link_count": body["link_count"],
        "right_cell_text": tag_text(right_cell),
        "right_cell_links": extract_links(right_cell),
        "caption_text": tag_text(caption_cell),
        "caption_sections": caption_sections,
        "products_text": caption_sections.get("Products", ""),
        "why_is_this_here_text": caption_sections.get("Why is this here?", ""),
        "content_cells": content_cells_data,
        "raw_html": fragment,
    }


def iter_fragments(html_text: str) -> list[str]:
    parts = html_text.split(OUTER_CELL_SPLIT)[1:]
    return [OUTER_CELL_SPLIT + part for part in parts]


def write_jsonl(records: list[dict[str, Any]], output_path: Path) -> None:
    with output_path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def write_csv(records: list[dict[str, Any]], output_path: Path) -> None:
    flat_records = []
    for record in records:
        flat_records.append(
            {
                "activity_id": record["activity_id"],
                "service": record["service"],
                "action": record["action"],
                "timestamp_text": record["timestamp_text"],
                "timestamp_iso": record["timestamp_iso"],
                "detail_text": record["detail_text"],
                "primary_text": record["primary_text"],
                "primary_url": record["primary_url"],
                "secondary_text": record["secondary_text"],
                "secondary_url": record["secondary_url"],
                "body_text": record["body_text"],
                "body_link_count": record["body_link_count"],
                "right_cell_text": record["right_cell_text"],
                "caption_text": record["caption_text"],
                "products_text": record["products_text"],
                "why_is_this_here_text": record["why_is_this_here_text"],
                "detail_lines_json": json.dumps(record["detail_lines"], ensure_ascii=False),
                "body_lines_json": json.dumps(record["body_lines"], ensure_ascii=False),
                "body_links_json": json.dumps(record["body_links"], ensure_ascii=False),
                "right_cell_links_json": json.dumps(record["right_cell_links"], ensure_ascii=False),
                "caption_sections_json": json.dumps(record["caption_sections"], ensure_ascii=False),
                "content_cells_json": json.dumps(record["content_cells"], ensure_ascii=False),
            }
        )

    fieldnames = list(flat_records[0].keys()) if flat_records else []
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(flat_records)


def build_outputs(html_path: Path, output_dir: Path) -> tuple[Path, Path, int]:
    html_text = html_path.read_text(encoding="utf-8")
    fragments = iter_fragments(html_text)
    records = [parse_entry(index, fragment) for index, fragment in enumerate(fragments, start=1)]

    output_dir.mkdir(parents=True, exist_ok=True)
    csv_path = output_dir / f"{html_path.stem}.csv"
    jsonl_path = output_dir / f"{html_path.stem}.jsonl"

    write_csv(records, csv_path)
    write_jsonl(records, jsonl_path)
    return csv_path, jsonl_path, len(records)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert Google My Activity HTML exports into CSV and JSONL."
    )
    parser.add_argument(
        "--input",
        default=str(DEFAULT_INPUT),
        help="Path to the Google My Activity HTML file.",
    )
    parser.add_argument(
        "--output-dir",
        default=str(DEFAULT_OUTPUT_DIR),
        help="Directory where the CSV and JSONL files will be written.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    html_path = Path(args.input)
    output_dir = Path(args.output_dir)

    if not html_path.is_file():
        raise FileNotFoundError(f"Input file not found: {html_path}")

    csv_path, jsonl_path, row_count = build_outputs(html_path, output_dir)
    print(f"Converted {row_count} activities")
    print(f"CSV:   {csv_path}")
    print(f"JSONL: {jsonl_path}")


if __name__ == "__main__":
    main()
