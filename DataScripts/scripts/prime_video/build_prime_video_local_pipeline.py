#!/usr/bin/env python3
"""Run the local Prime Video pipeline from raw export to reusable public outputs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from build_prime_video_dataset import build_outputs as build_processed_outputs
from build_prime_video_fine_processed import build_outputs as build_fine_outputs
from build_prime_video_public_dataset import build_outputs as build_public_outputs


REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_RAW_PATH = REPO_ROOT / "data_local" / "raw" / "prime_video" / "raw.txt"
DEFAULT_PROCESSED_OUTPUT_DIR = REPO_ROOT / "data_local" / "processed" / "prime_video"
DEFAULT_FINE_OUTPUT_DIR = REPO_ROOT / "data_local" / "fine_processed"
DEFAULT_LOCAL_PUBLIC_OUTPUT_DIR = REPO_ROOT / "data_local" / "adjusted_local" / "prime_video_public"
DEFAULT_PUBLIC_OUTPUT_DIR = REPO_ROOT / "data_github" / "prime_video_public"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build local Prime Video processed, fine_processed, and public outputs."
    )
    parser.add_argument(
        "--raw-path",
        default=str(DEFAULT_RAW_PATH),
        help="Path to the Prime Video pasted raw text file.",
    )
    parser.add_argument(
        "--processed-output-dir",
        default=str(DEFAULT_PROCESSED_OUTPUT_DIR),
        help="Directory where processed Prime Video outputs will be written.",
    )
    parser.add_argument(
        "--fine-output-dir",
        default=str(DEFAULT_FINE_OUTPUT_DIR),
        help="Directory where fine_processed Prime Video outputs will be written.",
    )
    parser.add_argument(
        "--local-public-output-dir",
        default=str(DEFAULT_LOCAL_PUBLIC_OUTPUT_DIR),
        help="Directory where the local public mirror will be written.",
    )
    parser.add_argument(
        "--public-output-dir",
        default=str(DEFAULT_PUBLIC_OUTPUT_DIR),
        help="Directory where the public Prime Video release will be written.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    raw_path = Path(args.raw_path)
    processed_output_dir = Path(args.processed_output_dir)
    fine_output_dir = Path(args.fine_output_dir)
    local_public_output_dir = Path(args.local_public_output_dir)
    public_output_dir = Path(args.public_output_dir)

    processed_summary = build_processed_outputs(
        raw_path=raw_path,
        output_dir=processed_output_dir,
    )

    fine_summary = build_fine_outputs(
        input_csv=processed_output_dir / "prime_video_watch_history.csv",
        output_dir=fine_output_dir,
    )

    public_summary = build_public_outputs(
        input_csv=fine_output_dir / "fine_prime_video_watch_history_local.csv",
        local_output_dir=local_public_output_dir,
        public_output_dir=public_output_dir,
    )

    print(
        json.dumps(
            {
                "processed": processed_summary,
                "fine_processed": fine_summary,
                "public_release": public_summary,
            },
            indent=2,
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
