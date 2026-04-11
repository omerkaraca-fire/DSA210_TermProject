# Prime Video Scripts

This folder contains the Prime Video-specific pipeline for the project.

The scripts are meant to be read in this order:

1. `build_prime_video_dataset.py`
2. `build_prime_video_fine_processed.py`
3. `build_prime_video_public_dataset.py`
4. `build_prime_video_local_pipeline.py`

## Main Idea

The Prime Video flow turns the pasted watch-history text export into a cleaned
row-level watch-history table, then into the shared fine layer, and finally into
the public release.

In practice the full flow is:

`raw export -> processed -> fine_processed -> public`

## Script Summary

### `build_prime_video_dataset.py`

Builds the main processed Prime Video watch-history table from the raw text dump.

What it does:
- parses the pasted Prime Video watch-history text
- keeps one row per inferred watch event
- writes local parse-quality files for debugging
- counts parse issues in the build summary

Main input:
- `data_local/raw/prime_video/raw.txt`

Main outputs:
- `data_local/processed/prime_video/prime_video_watch_history.csv`
- `data_local/processed/prime_video/prime_video_watch_history.jsonl`
- `data_local/processed/prime_video/build_summary.json`

### `build_prime_video_fine_processed.py`

Converts the processed Prime Video table into the project-wide fine format.

What it does:
- reads the processed Prime Video watch-history CSV
- adds the shared `fine_*` columns
- keeps the dataset row-level for later EDA and testing

Main input:
- `data_local/processed/prime_video/prime_video_watch_history.csv`

Main outputs:
- `data_local/fine_processed/fine_prime_video_watch_history_local.csv`
- `data_local/fine_processed/fine_prime_video_watch_history_local.jsonl`

### `build_prime_video_public_dataset.py`

Builds the moderate-masked Prime Video public release from the fine layer.

What it does:
- reads the local fine Prime Video file
- keeps titles visible for analysis
- masks the source-file reference
- writes the same release to GitHub and the local mirror

Main input:
- `data_local/fine_processed/fine_prime_video_watch_history_local.csv`

Main outputs:
- `data_github/prime_video_public/prime_video_watch_history_public.csv`
- `data_github/prime_video_public/prime_video_watch_history_public.jsonl`
- matching local mirror under `data_local/adjusted_local/prime_video_public`

### `build_prime_video_local_pipeline.py`

Wrapper script for the full Prime Video pipeline.

What it does:
- runs `build_prime_video_dataset.py`
- runs `build_prime_video_fine_processed.py`
- runs `build_prime_video_public_dataset.py`
- prints one combined summary at the end

Use this when you want the whole Prime Video flow from raw export to final
public release in one command.

## Recommended Command

Run the full pipeline from the repository root:

```bash
python3 DataScripts/scripts/prime_video/build_prime_video_local_pipeline.py
```

## When To Run Which Script

Use `build_prime_video_local_pipeline.py`:
- when the raw Prime Video export changed
- when you want to rebuild everything

Use `build_prime_video_public_dataset.py`:
- when only the public release logic changed
- when the local fine Prime Video file already exists

Use `build_prime_video_dataset.py`:
- when you are checking the raw text parsing or processed output
