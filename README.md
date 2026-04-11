# DSA210_TermProject
This repository contains the term project for the course DSA210.

Author - Nihat Ömer Karaca  
E-mail - omer.karaca@sabanciuniv.edu or nihatomer.karaca@gmail.com

This project studies how my entertainment behavior changes under academic pressure. The current public version focuses on four entertainment platforms: YouTube, Spotify, Netflix, and Prime Video. These datasets are combined with an academic calendar so the later analysis can compare ordinary term days, final-exam periods, and seasonal term differences.

The private raw exports were not equally clean or equally easy to use. Some platforms gave structured JSON or CSV files, while others needed more careful parsing and privacy handling. For that reason, this README describes the public prepared data and the general cleaning logic, not the private local raw folders.

## Raw Data / Public Data

| Dataset | Public output | Current public size | Date range | Notes |
|---|---|---:|---|---|
| YouTube | `data_github/youtube_public/` | 34,317 activity rows and 22 subscription rows | 2022-04-17 to 2026-03-15 | Google Takeout activity converted into public activity and subscription tables. |
| Spotify | `data_github/spotify_public/` | 178,202 streaming rows | 2019-07-27 to 2026-03-14 | Music-focused streaming history with timestamps and listening duration. |
| Netflix | `data_github/netflix_public/` | 2,493 viewing rows | 2020-02-25 to 2026-03-10 | Viewing-history data kept at row level with titles visible. |
| Prime Video | `data_github/prime_video_public/` | 719 watch-history rows | 2022-03-30 to 2026-03-19 | Watch-history data parsed into movie and episode records with titles visible. |
| Academic calendar | `data_github/academical_calendar/` | Calendar labels | 2021-2022 to 2025-2026 | Used as the label source for term, add-drop, week, and final-exam periods. |

## Methodology

The project will use the day as the main unit of analysis because all current public datasets can be joined by `fine_date`. This makes it possible to compare activity across platforms even though the raw platforms do not measure behavior in the same way. Spotify has duration, YouTube has timestamped activity events, and Netflix and Prime Video mainly provide date-level viewing records.

The later EDA will first inspect each dataset separately, then create a cross-platform daily panel. In that panel, Netflix and Prime Video can be grouped as long-form streaming while still staying separate in their public release files.

## Data Cleaning & Integration

Each platform was converted into a public analysis-ready format through platform-specific scripts. The scripts follow the same general flow: raw export to processed data, processed data to `fine_*` fields, then a reduced public dataset under `data_github/`.

Private identifiers and local paths were masked or removed before public release. Timestamps were preserved where the platform provided them. Netflix titles were not split into show, season, and episode fields because the title strings are not consistent enough to parse safely at this stage. Prime Video records were parsed into movie and episode fields where possible, while parse uncertainty is tracked in local summaries instead of being exposed as a separate public table.

## Visualization

This section will be added after the EDA notebooks or scripts are created.

## Hypothesis Test

These hypotheses are the current planned directions. They are not final results yet.

| Hypothesis | H0 | H1 | Variables |
|---|---|---|---|
| Entertainment usage during academic pressure | Daily entertainment usage does not differ between final-exam days and ordinary term days. | Daily entertainment usage is lower during final-exam days. | YouTube watch count, Spotify hours, Netflix count, Prime Video count |
| Platform diversity during academic pressure | The number of entertainment platforms used per day does not differ between final-exam days and ordinary term days. | Platform diversity is lower during final-exam days. | Distinct active entertainment platforms per day |
| Long-form streaming and YouTube activity | YouTube watch activity does not differ between long-form streaming active and inactive days. | YouTube watch activity is lower on long-form streaming active days. | Netflix count, Prime Video count, YouTube watch count |
| Spotify and YouTube co-usage | Daily Spotify listening is not positively associated with daily YouTube watch activity. | Higher Spotify listening is positively associated with higher YouTube watch activity. | Spotify hours, YouTube watch count |
| After-9:30 PM entertainment during finals | After-9:30 PM entertainment share does not differ between final-exam days and ordinary term days. | After-9:30 PM entertainment share is lower during final-exam days. | YouTube and Spotify activity between 21:30 and 04:59 |
| Optional seasonal entertainment mix | Entertainment platform mix does not differ across fall, spring, and summer terms. | Summer terms have higher Spotify share and lower YouTube activity. | Term label, Spotify hours, YouTube count, long-form streaming count |

## Repository Structure

The structure below reflects the current GitHub-facing repository layout.

```text
DSA210_TermProject/
├── DataScripts/
│   └── scripts/
│       ├── netflix/
│       ├── prime_video/
│       ├── spotify/
│       └── youtube/
├── Reports/
│   ├── .gitignore
│   └── proposal.pdf
├── data_github/
│   ├── academical_calendar/
│   ├── netflix_public/
│   ├── prime_video_public/
│   ├── spotify_public/
│   └── youtube_public/
├── .gitignore
├── LICENSE
├── ProjectRequirements.txt
└── README.md
```
