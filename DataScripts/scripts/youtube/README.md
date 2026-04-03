# YouTube Scripts

This folder contains the YouTube-specific pipeline for the project.

The scripts are meant to be read in this order:

1. `convert_my_activity.py`
2. `build_youtube_activity_dataset.py`
3. `build_youtube_fine_processed.py`
4. `build_youtube_public_chunks.py`
5. `build_youtube_local_pipeline.py`

## Main Idea

The YouTube flow goes from raw exports to processed local tables, then to the
shared fine layer, and finally to the anonymized public release.

In practice the full flow is:

`raw export -> processed -> fine_processed -> public`

## Script Summary

### `convert_my_activity.py`

Low-level parser for Google My Activity HTML.

What it does:
- reads a single My Activity HTML file
- extracts one activity entry at a time
- pulls out action, timestamp, primary text, secondary text, URLs, caption data,
  and other raw structured fields

Typical use:
- used by `build_youtube_activity_dataset.py`
- mainly helpful when parsing the legacy fallback export

Main input:
- `data_local/raw/youtube_legacy/MyActivity.html`

Main output:
- parsed in-memory rows, or CSV/JSONL if run directly

### `build_youtube_activity_dataset.py`

Builds the main processed YouTube tables from raw account exports.

What it does:
- reads both YouTube account folders under `data_local/raw`
- parses `watch-history.html`
- parses `search-history.html`
- reads `subscriptions.csv`
- merges the two accounts
- removes duplicates
- optionally fills missing rows from the legacy My Activity export

Main inputs:
- `data_local/raw/youtube_account_*/YouTube and YouTube Music/...`
- optional `data_local/raw/youtube_legacy/MyActivity.html`

Main outputs:
- `data_local/processed/combined/youtube_activity_merged.csv`
- `data_local/processed/combined/subscriptions_merged.csv`
- per-account processed files and build summary

### `build_youtube_fine_processed.py`

Converts the processed YouTube tables into the project-wide fine format.

What it does:
- reads the merged processed activity and subscriptions tables
- adds the shared `fine_*` columns
- normalizes dates and timestamps into the common structure
- writes local fine CSV, JSONL, and chunked files

Main inputs:
- `data_local/processed/combined/youtube_activity_merged.csv`
- `data_local/processed/combined/subscriptions_merged.csv`

Main outputs:
- `data_local/fine_processed/fine_youtube_activity_local.csv`
- `data_local/fine_processed/fine_youtube_subscriptions_local.csv`
- chunked CSV/JSONL versions and summary file

### `build_youtube_public_chunks.py`

Builds the anonymized public YouTube release from the fine layer.

What it does:
- reads the local fine YouTube files
- replaces identifying values with stable internal IDs
- keeps exact timestamps for analysis
- creates public activity and subscriptions files
- writes chunked CSV/JSONL outputs
- mirrors the same release under `data_local/adjusted_local`

Main inputs:
- `data_local/fine_processed/fine_youtube_activity_local.csv`
- `data_local/fine_processed/fine_youtube_subscriptions_local.csv`

Main outputs:
- `data_github/youtube_public/youtube_activity_public.csv`
- `data_github/youtube_public/youtube_subscriptions_public.csv`
- matching local mirror under `data_local/adjusted_local/youtube_public`

### `build_youtube_local_pipeline.py`

Wrapper script for the full YouTube pipeline.

What it does:
- runs `build_youtube_activity_dataset.py`
- runs `build_youtube_fine_processed.py`
- runs `build_youtube_public_chunks.py`
- prints one combined summary at the end

Use this when you want the whole YouTube flow from raw data to final public
release in one command.

## Recommended Command

Run the full pipeline from the repository root:

```bash
python3 DataScripts/scripts/youtube/build_youtube_local_pipeline.py
```

## When To Run Which Script

Use `build_youtube_local_pipeline.py`:
- when raw exports changed
- when you want to rebuild everything

Use `build_youtube_public_chunks.py`:
- when only the public release logic changed
- when the fine local YouTube files already exist

Use `build_youtube_activity_dataset.py`:
- when you are debugging raw parsing or merged processed outputs

Use `convert_my_activity.py`:
- when you need to inspect how the raw HTML parser behaves on a single export
