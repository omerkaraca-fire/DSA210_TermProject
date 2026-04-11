# Spotify Scripts

This folder contains the Spotify-specific pipeline for the project.

The scripts are meant to be read in this order:

1. `build_spotify_dataset.py`
2. `build_spotify_fine_processed.py`
3. `build_spotify_public_dataset.py`
4. `build_spotify_local_pipeline.py`

## Main Idea

The Spotify flow keeps the release focused on music listening so the dataset
stays useful for later EDA and hypothesis testing without pulling in extra
podcast or video complexity.

In practice the full flow is:

`raw export -> processed -> fine_processed -> public`

## Script Summary

### `build_spotify_dataset.py`

Builds the main processed Spotify table from the raw extended streaming export.

What it does:
- reads Spotify streaming-history JSON files from the raw account folder
- keeps only music-focused audio rows
- excludes podcast, audiobook, and Spotify video rows
- writes one processed row per kept listening event

Main input:
- `data_local/raw/spotify_account_*/Spotify Extended Streaming History/`

Main outputs:
- `data_local/processed/spotify/spotify_streaming_history_processed.csv`
- `data_local/processed/spotify/spotify_streaming_history_processed.jsonl`
- `data_local/processed/spotify/build_summary.json`

### `build_spotify_fine_processed.py`

Converts the processed Spotify table into the project-wide fine format.

What it does:
- reads the processed Spotify CSV
- adds the shared `fine_*` columns
- keeps exact timestamps and duration fields for later aggregation

Main input:
- `data_local/processed/spotify/spotify_streaming_history_processed.csv`

Main outputs:
- `data_local/fine_processed/fine_spotify_streaming_local.csv`
- `data_local/fine_processed/fine_spotify_streaming_local.jsonl`

### `build_spotify_public_dataset.py`

Builds the moderate-masked Spotify public release from the fine layer.

What it does:
- reads the local fine Spotify file
- keeps track, artist, album, timestamps, and duration visible
- masks account and source-file identifiers
- writes the same release to GitHub and the local mirror

Main input:
- `data_local/fine_processed/fine_spotify_streaming_local.csv`

Main outputs:
- `data_github/spotify_public/spotify_streaming_public.csv`
- `data_github/spotify_public/spotify_streaming_public.jsonl`
- matching local mirror under `data_local/adjusted_local/spotify_public`

### `build_spotify_local_pipeline.py`

Wrapper script for the full Spotify pipeline.

What it does:
- runs `build_spotify_dataset.py`
- runs `build_spotify_fine_processed.py`
- runs `build_spotify_public_dataset.py`
- prints one combined summary at the end

Use this when you want the whole Spotify flow from raw export to final public
release in one command.

## Recommended Command

Run the full pipeline from the repository root:

```bash
python3 DataScripts/scripts/spotify/build_spotify_local_pipeline.py
```

## When To Run Which Script

Use `build_spotify_local_pipeline.py`:
- when the raw Spotify export changed
- when you want to rebuild everything

Use `build_spotify_public_dataset.py`:
- when only the public release logic changed
- when the local fine Spotify file already exists

Use `build_spotify_dataset.py`:
- when you are checking the raw JSON structure or processed output
