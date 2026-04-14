#!/usr/bin/env python3
"""Split a JSONL file into smaller chunk files."""

from __future__ import annotations

import argparse
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_INPUT = PROJECT_ROOT / "data" / "processed" / "combined" / "youtube_activity_merged.jsonl"
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "data" / "processed" / "combined" / "chunks"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Split a JSONL file into smaller files.")
    parser.add_argument(
        "--input",
        default=str(DEFAULT_INPUT),
        help="Path to the source JSONL file.",
    )
    parser.add_argument(
        "--lines-per-file",
        type=int,
        default=1000,
        help="Number of JSONL records to write to each chunk.",
    )
    parser.add_argument(
        "--output-dir",
        default=str(DEFAULT_OUTPUT_DIR),
        help="Directory where chunk files will be written.",
    )
    parser.add_argument(
        "--prefix",
        default=None,
        help="Optional filename prefix for chunk files. Defaults to the input stem.",
    )
    return parser.parse_args()


def split_jsonl(input_path: Path, output_dir: Path, lines_per_file: int, prefix: str | None = None) -> int:
    if lines_per_file <= 0:
        raise ValueError("--lines-per-file must be greater than zero")

    output_dir.mkdir(parents=True, exist_ok=True)

    chunk_index = 0
    line_index = 0
    handle = None

    try:
        with input_path.open("r", encoding="utf-8") as source:
            for raw_line in source:
                if line_index % lines_per_file == 0:
                    if handle is not None:
                        handle.close()
                    chunk_index += 1
                    chunk_label = prefix or input_path.stem
                    chunk_name = f"{chunk_label}_part_{chunk_index:03d}.jsonl"
                    handle = (output_dir / chunk_name).open("w", encoding="utf-8")

                handle.write(raw_line)
                line_index += 1
    finally:
        if handle is not None:
            handle.close()

    return chunk_index


def main() -> None:
    args = parse_args()
    input_path = Path(args.input)
    output_dir = Path(args.output_dir)

    if not input_path.is_file():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    chunk_count = split_jsonl(input_path, output_dir, args.lines_per_file, prefix=args.prefix)
    print(f"Created {chunk_count} chunk files in {output_dir}")


if __name__ == "__main__":
    main()
