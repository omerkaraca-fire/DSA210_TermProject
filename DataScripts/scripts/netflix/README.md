# Netflix Scripts

This folder contains the Netflix-specific pipeline for the project.

The scripts are meant to be read in this order:

1. `build_netflix_viewing_dataset.py`
2. `build_netflix_fine_processed.py`
3. `build_netflix_public_dataset.py`
4. `build_netflix_local_pipeline.py`

## Main Idea

The Netflix flow is intentionally simple because the raw export is already a
single row-level CSV.

In practice the full flow is:

`raw export -> processed -> fine_processed -> public`

## Script Summary

### `build_netflix_viewing_dataset.py`

Builds the main processed Netflix viewing-history table from the raw CSV export.

What it does:
- reads `NetflixViewingHistory.csv`
- keeps one row per raw viewing-history row
- parses the export date into ISO format
- keeps the original title text without trying to split it

Main input:
- `data_local/raw/netflix/NetflixViewingHistory.csv`

Main outputs:
- `data_local/processed/netflix/netflix_viewing_history_processed.csv`
- `data_local/processed/netflix/netflix_viewing_history_processed.jsonl`
- `data_local/processed/netflix/build_summary.json`

### `build_netflix_fine_processed.py`

Converts the processed Netflix table into the project-wide fine format.

What it does:
- reads the processed Netflix CSV
- adds the shared `fine_*` columns
- keeps the dataset row-level for later EDA and testing

Main input:
- `data_local/processed/netflix/netflix_viewing_history_processed.csv`

Main outputs:
- `data_local/fine_processed/fine_netflix_viewing_history_local.csv`
- `data_local/fine_processed/fine_netflix_viewing_history_local.jsonl`

### `build_netflix_public_dataset.py`

Builds the moderate-masked Netflix public release from the fine layer.

What it does:
- reads the local fine Netflix file
- keeps titles visible for analysis
- masks the source-file reference
- writes the same release to GitHub and the local mirror

Main input:
- `data_local/fine_processed/fine_netflix_viewing_history_local.csv`

Main outputs:
- `data_github/netflix_public/netflix_viewing_public.csv`
- `data_github/netflix_public/netflix_viewing_public.jsonl`
- matching local mirror under `data_local/adjusted_local/netflix_public`

### `build_netflix_local_pipeline.py`

Wrapper script for the full Netflix pipeline.

What it does:
- runs `build_netflix_viewing_dataset.py`
- runs `build_netflix_fine_processed.py`
- runs `build_netflix_public_dataset.py`
- prints one combined summary at the end

Use this when you want the whole Netflix flow from raw export to final public
release in one command.

## Recommended Command

Run the full pipeline from the repository root:

```bash
python3 DataScripts/scripts/netflix/build_netflix_local_pipeline.py
```

## When To Run Which Script

Use `build_netflix_local_pipeline.py`:
- when the raw Netflix export changed
- when you want to rebuild everything

Use `build_netflix_public_dataset.py`:
- when only the public release logic changed
- when the local fine Netflix file already exists

Use `build_netflix_viewing_dataset.py`:
- when you are checking the raw CSV structure or processed output
