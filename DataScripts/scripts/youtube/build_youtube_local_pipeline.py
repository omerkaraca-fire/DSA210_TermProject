#!/usr/bin/env python3
"""Run the local YouTube pipeline from raw exports to reusable fine_processed outputs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from build_youtube_activity_dataset import build_outputs as build_processed_outputs
from build_youtube_fine_processed import build_outputs as build_fine_outputs
from build_youtube_public_chunks import build_outputs as build_adjusted_outputs


REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_RAW_DIR = REPO_ROOT / "data_local" / "raw"
DEFAULT_PROCESSED_OUTPUT_DIR = REPO_ROOT / "data_local" / "processed"
DEFAULT_FINE_OUTPUT_DIR = REPO_ROOT / "data_local" / "fine_processed"
DEFAULT_ADJUSTED_LOCAL_OUTPUT_DIR = REPO_ROOT / "data_local" / "adjusted_local" / "youtube_public"
DEFAULT_PUBLIC_OUTPUT_DIR = REPO_ROOT / "data_github" / "youtube_public"
DEFAULT_LEGACY_PATH = DEFAULT_RAW_DIR / "youtube_legacy" / "MyActivity.html"
DEFAULT_FINE_ROWS_PER_FILE = 5000


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build local YouTube processed and fine_processed outputs."
    )
    parser.add_argument(
        "--raw-dir",
        default=str(DEFAULT_RAW_DIR),
        help="Directory that contains the raw YouTube export folders.",
    )
    parser.add_argument(
        "--processed-output-dir",
        default=str(DEFAULT_PROCESSED_OUTPUT_DIR),
        help="Directory where processed YouTube outputs will be written.",
    )
    parser.add_argument(
        "--fine-output-dir",
        default=str(DEFAULT_FINE_OUTPUT_DIR),
        help="Directory where fine_processed YouTube outputs will be written.",
    )
    parser.add_argument(
        "--adjusted-local-output-dir",
        default=str(DEFAULT_ADJUSTED_LOCAL_OUTPUT_DIR),
        help="Directory where the local mirrored YouTube public release will be written.",
    )
    parser.add_argument(
        "--public-output-dir",
        default=str(DEFAULT_PUBLIC_OUTPUT_DIR),
        help="Directory where the YouTube public release will be written.",
    )
    parser.add_argument(
        "--legacy-path",
        default=str(DEFAULT_LEGACY_PATH),
        help="Optional legacy MyActivity.html export used as a fallback for uncovered records.",
    )
    parser.add_argument(
        "--skip-legacy-fallback",
        action="store_true",
        help="Ignore the legacy MyActivity.html export even if it exists.",
    )
    parser.add_argument(
        "--lines-per-chunk",
        type=int,
        default=1000,
        help="Number of JSONL records per chunk file in processed outputs.",
    )
    parser.add_argument(
        "--fine-rows-per-file",
        type=int,
        default=DEFAULT_FINE_ROWS_PER_FILE,
        help="Number of activity records per chunk file in fine_processed outputs.",
    )
    parser.add_argument(
        "--skip-adjusted-release",
        action="store_true",
        help="Skip building the local/public YouTube release mirror.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    raw_dir = Path(args.raw_dir)
    processed_output_dir = Path(args.processed_output_dir)
    fine_output_dir = Path(args.fine_output_dir)
    adjusted_local_output_dir = Path(args.adjusted_local_output_dir)
    public_output_dir = Path(args.public_output_dir)
    legacy_path = Path(args.legacy_path)

    processed_summary = build_processed_outputs(
        raw_dir=raw_dir,
        output_dir=processed_output_dir,
        legacy_path=legacy_path,
        use_legacy_fallback=not args.skip_legacy_fallback,
        lines_per_chunk=args.lines_per_chunk,
    )

    fine_summary = build_fine_outputs(
        activity_input=processed_output_dir / "combined" / "youtube_activity_merged.csv",
        subscriptions_input=processed_output_dir / "combined" / "subscriptions_merged.csv",
        output_dir=fine_output_dir,
        activity_rows_per_file=args.fine_rows_per_file,
    )

    summary = {
        "processed": processed_summary,
        "fine_processed": fine_summary,
    }

    if not args.skip_adjusted_release:
        adjusted_summary = build_adjusted_outputs(
            activity_input=fine_output_dir / "fine_youtube_activity_local.csv",
            subscriptions_input=fine_output_dir / "fine_youtube_subscriptions_local.csv",
            local_output_dir=adjusted_local_output_dir,
            public_output_dir=public_output_dir,
            activity_rows_per_file=args.fine_rows_per_file,
        )
        summary["adjusted_release"] = adjusted_summary

    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
