#!/usr/bin/env python3
"""Build the Netflix public release and mirror it locally/publicly."""

from __future__ import annotations

import argparse
import csv
import filecmp
import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_INPUT = REPO_ROOT / "data_local" / "fine_processed" / "fine_netflix_viewing_history_local.csv"
DEFAULT_LOCAL_OUTPUT_DIR = REPO_ROOT / "data_local" / "adjusted_local" / "netflix_public"
DEFAULT_PUBLIC_OUTPUT_DIR = REPO_ROOT / "data_github" / "netflix_public"

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
    "title",
    "title_missing",
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
        description="Build the Netflix public release and mirror it to local/public outputs."
    )
    parser.add_argument(
        "--input-csv",
        default=str(DEFAULT_INPUT),
        help="Path to the local fine_processed Netflix CSV.",
    )
    parser.add_argument(
        "--local-output-dir",
        default=str(DEFAULT_LOCAL_OUTPUT_DIR),
        help="Directory where the local public mirror will be written.",
    )
    parser.add_argument(
        "--public-output-dir",
        default=str(DEFAULT_PUBLIC_OUTPUT_DIR),
        help="Directory where the public Netflix release will be written.",
    )
    return parser.parse_args()


def safe_text(value: str | None) -> str:
    return (value or "").strip()


def load_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def build_public_rows(rows: list[dict[str, str]]) -> tuple[list[dict[str, str]], StableIdRegistry]:
    registry = StableIdRegistry()
    public_rows: list[dict[str, str]] = []

    for index, row in enumerate(rows, start=1):
        record_id = safe_text(row.get("fine_record_id")) or f"netflix_view_{index:06d}"

        # Keep titles visible for analysis, but replace the source file with a stable reference.
        public_rows.append(
            {
                "fine_platform": "netflix",
                "fine_table": "netflix_viewing_public",
                "fine_record_id": record_id,
                "fine_account": "",
                "fine_source_file": registry.get_id(
                    "source", safe_text(row.get("fine_source_file"))
                ),
                "fine_time_start": safe_text(row.get("fine_time_start")),
                "fine_time_end": safe_text(row.get("fine_time_end")),
                "fine_time_granularity": safe_text(row.get("fine_time_granularity")),
                "fine_date": safe_text(row.get("fine_date")),
                "title": safe_text(row.get("title")),
                "title_missing": "true"
                if safe_text(row.get("title_missing")).lower() == "true"
                else "false",
            }
        )

    return public_rows, registry


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


def write_release(output_dir: Path, rows: list[dict[str, str]], summary_payload: dict[str, Any]) -> None:
    csv_output = output_dir / "netflix_viewing_public.csv"
    jsonl_output = output_dir / "netflix_viewing_public.jsonl"
    summary_output = output_dir / "netflix_public_summary.json"

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
        raise FileNotFoundError(f"Fine Netflix input not found: {input_csv}")

    public_rows, registry = build_public_rows(load_rows(input_csv))

    summary_payload = {
        "dataset": "netflix_viewing_public",
        "row_count": len(public_rows),
        "invalid_date_count": sum(1 for row in public_rows if not row["fine_date"]),
        "title_missing_count": sum(1 for row in public_rows if row["title_missing"] == "true"),
        "date_range": date_range(public_rows),
        "source_file_reference_count": registry.namespace_size("source"),
        "files": {
            "csv": "netflix_viewing_public.csv",
            "jsonl": "netflix_viewing_public.jsonl",
            "summary": "netflix_public_summary.json",
        },
        "schema": OUTPUT_FIELDS,
    }

    write_release(local_output_dir, public_rows, summary_payload)
    write_release(public_output_dir, public_rows, summary_payload)

    # The public folder and local mirror should stay byte-identical in this step.
    mirrored_files = {
        "csv": (
            local_output_dir / "netflix_viewing_public.csv",
            public_output_dir / "netflix_viewing_public.csv",
        ),
        "jsonl": (
            local_output_dir / "netflix_viewing_public.jsonl",
            public_output_dir / "netflix_viewing_public.jsonl",
        ),
        "summary": (
            local_output_dir / "netflix_public_summary.json",
            public_output_dir / "netflix_public_summary.json",
        ),
    }

    return {
        "input_csv": str(input_csv),
        "local_output_dir": str(local_output_dir),
        "public_output_dir": str(public_output_dir),
        "row_count": summary_payload["row_count"],
        "invalid_date_count": summary_payload["invalid_date_count"],
        "title_missing_count": summary_payload["title_missing_count"],
        "source_file_reference_count": summary_payload["source_file_reference_count"],
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
