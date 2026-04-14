from __future__ import annotations

import json
import math
import shutil
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats


APP_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = APP_ROOT.parent
PUBLIC_DIR = APP_ROOT / "public"
DATA_DIR = PUBLIC_DIR / "data"
IMAGE_DIR = PUBLIC_DIR / "eda-images"

ALPHA = 0.05
TIMEZONE = "Europe/Istanbul"
AFTER_2130_START = 21 * 60 + 30
AFTER_2130_END = 5 * 60


DATASETS = [
    {
        "id": "youtube",
        "name": "YouTube",
        "role": "Short-form and mixed video behavior",
        "path": REPO_ROOT / "data_github/youtube_public/youtube_activity_public.csv",
        "publicPath": "data_github/youtube_public/",
        "color": "#5db5f0",
        "notes": "Google Takeout activity converted into a public activity table. Channel names are masked.",
    },
    {
        "id": "spotify",
        "name": "Spotify",
        "role": "Music listening duration",
        "path": REPO_ROOT / "data_github/spotify_public/spotify_streaming_public.csv",
        "publicPath": "data_github/spotify_public/",
        "color": "#7dd7ba",
        "notes": "Music-focused streaming history with exact timestamps and listening duration.",
    },
    {
        "id": "netflix",
        "name": "Netflix",
        "role": "Long-form viewing",
        "path": REPO_ROOT / "data_github/netflix_public/netflix_viewing_public.csv",
        "publicPath": "data_github/netflix_public/",
        "color": "#d29355",
        "notes": "Viewing history kept at row level. Titles stay visible; local source paths are not exposed.",
    },
    {
        "id": "prime-video",
        "name": "Prime Video",
        "role": "Long-form viewing",
        "path": REPO_ROOT / "data_github/prime_video_public/prime_video_watch_history_public.csv",
        "publicPath": "data_github/prime_video_public/",
        "color": "#f0c96a",
        "notes": "Watch history parsed into movie and episode records where possible.",
    },
]

IMAGE_FOLDERS = {
    "youtube": ("YouTube", REPO_ROOT / "EDA/youtube_images", IMAGE_DIR / "youtube"),
    "spotify": ("Spotify", REPO_ROOT / "EDA/spotify_images", IMAGE_DIR / "spotify"),
    "prime-netflix": (
        "Netflix + Prime Video",
        REPO_ROOT / "EDA/prime_netflix_images",
        IMAGE_DIR / "prime-netflix",
    ),
    "combined": ("Combined", REPO_ROOT / "EDA/combined_images", IMAGE_DIR / "combined"),
}

CURATED_PLOTS = {
    "combined_dataset_date_coverage.png",
    "combined_active_days_by_platform.png",
    "combined_monthly_cross_platform_trends.png",
    "combined_relative_activity_by_analysis_period.png",
    "combined_daily_variable_correlation_heatmap.png",
    "combined_platform_activity_by_analysis_period_boxplots.png",
    "combined_after_2130_by_analysis_period_boxplots.png",
    "combined_spotify_hours_vs_youtube_watched_scatter.png",
    "combined_netflix_prime_vs_youtube_watched_scatter.png",
    "youtube_activity_count_by_hour.png",
    "youtube_daily_watched_and_search_counts.png",
    "spotify_monthly_listening_hours.png",
    "spotify_daily_streams_vs_hours.png",
    "spotify_listening_hours_by_hour.png",
    "monthly_combined_long_form_count.png",
    "total_long_form_count_by_platform_common_range.png",
}

PLOT_CAPTIONS = {
    "youtube_activity_count_by_action.png": "YouTube is dominated by watch activity, while searches are a smaller but useful secondary behavior.",
    "youtube_activity_count_by_hour.png": "Activity clusters in the evening and late night, supporting the after-21:30 analysis window.",
    "youtube_activity_count_by_target_kind.png": "Most rows target videos, so YouTube is treated mainly as a watch-history signal.",
    "youtube_daily_after_2130_watched_count.png": "Late-night watch counts are bursty, with large spikes in the later part of the timeline.",
    "youtube_daily_watched_and_search_counts.png": "Watched counts are much larger than search counts, and daily behavior is highly spiky.",
    "youtube_daily_watched_by_weekday_boxplot.png": "Weekday medians are fairly close, while outliers appear on every weekday.",
    "youtube_daily_watched_search_distribution.png": "Daily watch and search counts are right-skewed, so nonparametric tests are safer.",
    "youtube_daily_watched_vs_search_scatter.png": "Search tends to rise on heavier YouTube days, but watch activity is not driven only by search.",
    "youtube_eda_overview_panel.png": "A compact YouTube summary: spiky daily counts, late-night concentration, and smaller search behavior.",
    "youtube_monthly_after_2130_share.png": "The late-night share varies strongly by month and should be read together with total volume.",
    "youtube_monthly_watched_and_search_counts.png": "Monthly YouTube activity has visible peaks, especially around late 2024 and late 2025.",
    "youtube_top_masked_channel_refs.png": "A small set of masked channel references accounts for repeated activity, without revealing channel names.",
    "spotify_daily_after_2130_hours.png": "After-21:30 listening appears throughout the timeline and has repeated high-listening spikes.",
    "spotify_daily_hours_by_weekday_boxplot.png": "Spotify hours exist across all weekdays, with slightly higher weekend medians and many outliers.",
    "spotify_daily_hours_distribution.png": "Spotify daily hours are right-skewed, with many low-listening days and a few very high days.",
    "spotify_daily_listening_hours.png": "Daily Spotify listening becomes more consistent after 2021 and rises strongly across 2024-2025.",
    "spotify_daily_streams_vs_hours.png": "Daily stream count and listening hours move together strongly, but not perfectly.",
    "spotify_eda_overview_panel.png": "A compact Spotify summary: rising usage, skewed hours, strong stream-hour relation, and time-of-day structure.",
    "spotify_listening_hours_by_hour.png": "Spotify has a daytime block around late morning and a second evening/night block.",
    "spotify_monthly_listening_hours.png": "Monthly listening peaks in 2025, suggesting a longer-term habit shift beyond academic timing alone.",
    "spotify_top_15_artists_by_hours.png": "Listening is concentrated around a few artists, but content preference is not part of the main tests.",
    "spotify_top_15_tracks_by_hours.png": "Top tracks show repeated listening, but daily hours remain the cleaner testing variable.",
    "combined_long_form_distribution.png": "Netflix + Prime daily viewing is zero-heavy and bursty rather than a daily habit.",
    "combined_long_form_streaming_daily_count.png": "Long-form viewing appears in bursts, including a large Prime Video-driven spike in 2024.",
    "daily_count_distribution_active_days.png": "On active days, Netflix is generally more frequent than Prime Video, but both are bursty.",
    "daily_viewing_count_netflix_vs_prime.png": "Netflix and Prime Video spikes often appear in different periods, so they are grouped only at the EDA layer.",
    "long_form_daily_count_by_weekday_boxplot.png": "Weekday medians are zero, so weekday is not a strong long-form streaming explanation.",
    "long_form_streaming_by_platform.png": "Netflix is the more regular long-form platform, while Prime Video appears in shorter bursts.",
    "monthly_combined_long_form_count.png": "Monthly long-form streaming has strong peaks, especially around 2025-01.",
    "monthly_long_form_count_by_platform.png": "Netflix drives most large monthly peaks, while Prime Video contributes isolated bursts.",
    "netflix_title_quality_split.png": "Most Netflix titles are usable; malformed title rows are a small minority.",
    "netflix_vs_prime_daily_scatter.png": "Most active days belong to one service or the other, so same-day high usage is rare.",
    "prime_netflix_eda_overview_panel.png": "A compact long-form summary: sparse daily counts, weak same-day platform overlap, and episode-heavy Prime Video.",
    "prime_video_record_type_split.png": "Prime Video is mostly episode watching, with movies as a much smaller subset.",
    "top_15_netflix_title_groups.png": "Netflix viewing is concentrated in repeated series such as How I Met Your Mother and Friends.",
    "top_15_prime_video_title_groups.png": "Prime Video is also series-heavy, led by Supernatural and Game of Thrones.",
    "total_long_form_count_by_platform_common_range.png": "Netflix contributes more long-form rows than Prime Video in the common comparison range.",
    "combined_active_days_by_platform.png": "Spotify is the most continuous platform, while Netflix and Prime Video are sparse.",
    "combined_after_2130_by_analysis_period_boxplots.png": "Late-night YouTube and Spotify activity are lower during finals in the current basic tests.",
    "combined_daily_distribution_overview.png": "All main daily variables are skewed, especially YouTube counts and Netflix + Prime counts.",
    "combined_daily_variable_correlation_heatmap.png": "YouTube variables correlate with each other; Spotify variables correlate with each other; long-form viewing is weakly tied to both.",
    "combined_dataset_date_coverage.png": "The common comparison window is where all four public platform datasets overlap.",
    "combined_eda_overview_panel.png": "A compact cross-platform overview of monthly trends, platform diversity, and Spotify-YouTube scatter.",
    "combined_monthly_after_2130_activity.png": "Late-night YouTube and Spotify peaks happen in different months, so they are related but separate behaviors.",
    "combined_monthly_cross_platform_trends.png": "YouTube, Spotify, and Netflix + Prime peak in different months, showing different entertainment rhythms.",
    "combined_netflix_prime_vs_youtube_watched_scatter.png": "Netflix + Prime days do not show a strong same-day relationship with YouTube watched count.",
    "combined_platform_activity_by_analysis_period_boxplots.png": "Each platform metric is shown separately because the units differ across services.",
    "combined_platform_diversity_by_analysis_period.png": "Platform diversity is usually one or two active platforms per day, with modest period differences.",
    "combined_relative_activity_by_analysis_period.png": "Relative scaling shows ordinary term above usual YouTube activity and summer work above usual Spotify hours.",
    "combined_spotify_hours_vs_youtube_watched_scatter.png": "Spotify hours and YouTube watched count show a weak positive relationship rather than a strong linear pattern.",
}


def read_platform_data() -> dict[str, pd.DataFrame]:
    data = {dataset["id"]: pd.read_csv(dataset["path"]) for dataset in DATASETS}
    for frame in data.values():
        frame["fine_date"] = pd.to_datetime(frame["fine_date"])
    return data


def prepare_combined_daily(data: dict[str, pd.DataFrame]) -> tuple[pd.DataFrame, pd.Timestamp, pd.Timestamp]:
    youtube = data["youtube"].copy()
    spotify = data["spotify"].copy()
    netflix = data["netflix"].copy()
    prime = data["prime-video"].copy()
    calendar = pd.read_json(REPO_ROOT / "data_github/academical_calendar/academicCalendar.jsonl", lines=True)

    youtube["fine_time_start_dt"] = pd.to_datetime(
        youtube["fine_time_start"], errors="coerce", utc=True
    ).dt.tz_convert(TIMEZONE)
    spotify["fine_time_start_dt"] = pd.to_datetime(
        spotify["fine_time_start"], errors="coerce", utc=True
    ).dt.tz_convert(TIMEZONE)

    for frame in [youtube, spotify]:
        frame["minute_of_day"] = frame["fine_time_start_dt"].dt.hour * 60 + frame["fine_time_start_dt"].dt.minute
        frame["is_after_2130"] = (
            (frame["minute_of_day"] >= AFTER_2130_START) | (frame["minute_of_day"] < AFTER_2130_END)
        )

    common_start = max(frame["fine_date"].min() for frame in [youtube, spotify, netflix, prime])
    common_end = min(frame["fine_date"].max() for frame in [youtube, spotify, netflix, prime])
    all_dates = pd.DataFrame({"fine_date": pd.date_range(common_start, common_end, freq="D")})

    calendar_rows: list[dict[str, object]] = []
    for _, row in calendar.iterrows():
        term_start = pd.to_datetime(row["term_start_date"])
        final_start = pd.to_datetime(row["final_exam_start_date"])
        final_end = pd.to_datetime(row["final_exam_end_date"])
        for date_value in pd.date_range(term_start, final_end, freq="D"):
            academic_period = "final_exam" if final_start <= date_value <= final_end else "ordinary_term"
            analysis_period = "summer_work_period" if row["term"] == "summer" else academic_period
            calendar_rows.append({"fine_date": date_value, "analysis_period": analysis_period})
    calendar_daily = pd.DataFrame(calendar_rows).drop_duplicates("fine_date", keep="first")

    youtube_daily = (
        youtube.groupby("fine_date")
        .agg(
            youtube_daily_total_count=("fine_record_id", "count"),
            youtube_daily_watched_count=("action", lambda x: (x == "Watched").sum()),
            youtube_daily_search_count=("action", lambda x: (x == "Searched for").sum()),
            youtube_after_2130_count=("is_after_2130", "sum"),
        )
        .reset_index()
    )
    youtube_after = (
        youtube[youtube["is_after_2130"] & (youtube["action"] == "Watched")]
        .groupby("fine_date")
        .size()
        .reset_index(name="youtube_after_2130_watched_count")
    )
    youtube_daily = youtube_daily.merge(youtube_after, on="fine_date", how="left")
    watched_times = (
        youtube[(youtube["action"] == "Watched") & youtube["fine_time_start_dt"].notna()]
        .sort_values(["fine_date", "fine_time_start_dt"])
        .copy()
    )
    watched_times["next_watch_time"] = watched_times.groupby("fine_date")["fine_time_start_dt"].shift(-1)
    watched_times["gap_minutes"] = (
        watched_times["next_watch_time"] - watched_times["fine_time_start_dt"]
    ).dt.total_seconds() / 60
    watched_times["estimated_watch_minutes"] = watched_times["gap_minutes"].where(
        (watched_times["gap_minutes"] > 0) & (watched_times["gap_minutes"] <= 60),
        0,
    )
    youtube_estimated_watch = (
        watched_times.groupby("fine_date")["estimated_watch_minutes"]
        .sum()
        .reset_index(name="youtube_estimated_continuous_watch_minutes")
    )
    youtube_daily = youtube_daily.merge(youtube_estimated_watch, on="fine_date", how="left")

    spotify_daily = (
        spotify.groupby("fine_date")
        .agg(
            spotify_daily_hours=("hours_played", "sum"),
            spotify_daily_stream_count=("fine_record_id", "count"),
        )
        .reset_index()
    )
    spotify_after = (
        spotify[spotify["is_after_2130"]]
        .groupby("fine_date")
        .agg(
            spotify_after_2130_hours=("hours_played", "sum"),
            spotify_after_2130_stream_count=("fine_record_id", "count"),
        )
        .reset_index()
    )
    spotify_daily = spotify_daily.merge(spotify_after, on="fine_date", how="left")

    netflix_daily = netflix.groupby("fine_date").size().reset_index(name="netflix_daily_count")
    prime_daily = prime.groupby("fine_date").size().reset_index(name="prime_video_daily_count")

    for frame in [all_dates, calendar_daily, youtube_daily, spotify_daily, netflix_daily, prime_daily]:
        frame["fine_date"] = pd.to_datetime(frame["fine_date"])

    combined = (
        all_dates.merge(youtube_daily, on="fine_date", how="left")
        .merge(spotify_daily, on="fine_date", how="left")
        .merge(netflix_daily, on="fine_date", how="left")
        .merge(prime_daily, on="fine_date", how="left")
        .merge(calendar_daily, on="fine_date", how="left")
    )
    combined["analysis_period"] = combined["analysis_period"].fillna("outside_calendar")

    activity_columns = [
        column
        for column in combined.columns
        if column not in {"fine_date", "analysis_period"}
    ]
    combined[activity_columns] = combined[activity_columns].fillna(0)

    count_columns = [
        "youtube_daily_total_count",
        "youtube_daily_watched_count",
        "youtube_daily_search_count",
        "youtube_after_2130_count",
        "youtube_after_2130_watched_count",
        "spotify_daily_stream_count",
        "spotify_after_2130_stream_count",
        "netflix_daily_count",
        "prime_video_daily_count",
    ]
    for column in count_columns:
        combined[column] = combined[column].astype(int)

    combined["netflix_prime_daily_count"] = combined["netflix_daily_count"] + combined["prime_video_daily_count"]
    combined["netflix_prime_active_day"] = combined["netflix_prime_daily_count"] > 0
    combined["daily_distinct_entertainment_platform_count"] = (
        (combined["youtube_daily_total_count"] > 0).astype(int)
        + (combined["spotify_daily_stream_count"] > 0).astype(int)
        + (combined["netflix_daily_count"] > 0).astype(int)
        + (combined["prime_video_daily_count"] > 0).astype(int)
    )
    combined["youtube_after_2130_share"] = (
        combined["youtube_after_2130_count"] / combined["youtube_daily_total_count"].replace(0, np.nan)
    ).fillna(0)
    combined["spotify_after_2130_hour_share"] = (
        combined["spotify_after_2130_hours"] / combined["spotify_daily_hours"].replace(0, np.nan)
    ).fillna(0)

    return combined, common_start, common_end


def prepare_hourly_activity(data: dict[str, pd.DataFrame]) -> list[dict[str, object]]:
    youtube = data["youtube"].copy()
    spotify = data["spotify"].copy()

    youtube["fine_time_start_dt"] = pd.to_datetime(
        youtube["fine_time_start"], errors="coerce", utc=True
    ).dt.tz_convert(TIMEZONE)
    spotify["fine_time_start_dt"] = pd.to_datetime(
        spotify["fine_time_start"], errors="coerce", utc=True
    ).dt.tz_convert(TIMEZONE)

    youtube["hour"] = youtube["fine_time_start_dt"].dt.hour
    spotify["hour"] = spotify["fine_time_start_dt"].dt.hour
    youtube_watched = (
        youtube[youtube["action"] == "Watched"].groupby("hour").size().reindex(range(24), fill_value=0)
    )
    spotify_hours = spotify.groupby("hour")["hours_played"].sum().reindex(range(24), fill_value=0)

    return [
        {
            "hour": int(hour),
            "youtubeWatched": int(youtube_watched.loc[hour]),
            "spotifyHours": finite(spotify_hours.loc[hour]),
        }
        for hour in range(24)
    ]


def prepare_platform_eda(data: dict[str, pd.DataFrame], combined: pd.DataFrame) -> dict[str, object]:
    youtube = data["youtube"].copy()
    spotify = data["spotify"].copy()
    netflix = data["netflix"].copy()
    prime = data["prime-video"].copy()

    youtube["fine_time_start_dt"] = pd.to_datetime(
        youtube["fine_time_start"], errors="coerce", utc=True
    ).dt.tz_convert(TIMEZONE)
    spotify["fine_time_start_dt"] = pd.to_datetime(
        spotify["fine_time_start"], errors="coerce", utc=True
    ).dt.tz_convert(TIMEZONE)
    youtube["hour"] = youtube["fine_time_start_dt"].dt.hour
    spotify["hour"] = spotify["fine_time_start_dt"].dt.hour

    youtube_monthly = combined.copy()
    youtube_monthly["month"] = youtube_monthly["fine_date"].dt.to_period("M").dt.to_timestamp()
    youtube_monthly = (
        youtube_monthly.groupby("month")[["youtube_daily_watched_count", "youtube_daily_search_count"]]
        .sum()
        .reset_index()
    )
    youtube_estimated_monthly = (
        combined.assign(month=combined["fine_date"].dt.to_period("M").dt.to_timestamp())
        .groupby("month")["youtube_estimated_continuous_watch_minutes"]
        .sum()
        .div(60)
        .reset_index(name="youtube_estimated_continuous_watch_hours")
    )
    youtube_monthly = youtube_monthly.merge(youtube_estimated_monthly, on="month", how="left")
    youtube_hourly = (
        youtube.groupby("hour")
        .agg(
            total=("fine_record_id", "count"),
            watched=("action", lambda value: (value == "Watched").sum()),
            search=("action", lambda value: (value == "Searched for").sum()),
        )
        .reindex(range(24), fill_value=0)
        .reset_index()
    )

    spotify_monthly = spotify.copy()
    spotify_monthly["month"] = spotify_monthly["fine_date"].dt.to_period("M").dt.to_timestamp()
    spotify_monthly = (
        spotify_monthly.groupby("month")
        .agg(hours=("hours_played", "sum"), streams=("fine_record_id", "count"))
        .reset_index()
    )
    spotify_hourly = (
        spotify.groupby("hour")
        .agg(hours=("hours_played", "sum"), streams=("fine_record_id", "count"))
        .reindex(range(24), fill_value=0)
        .reset_index()
    )
    top_artists = (
        spotify.groupby("artist_name")["hours_played"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
        .sort_values()
        .reset_index()
    )
    spotify["track_artist_label"] = (
        spotify["track_name"].fillna("Unknown track").astype(str).str.strip()
        + " - "
        + spotify["artist_name"].fillna("Unknown artist").astype(str).str.strip()
    )
    top_tracks = (
        spotify.groupby("track_artist_label")["minutes_played"]
        .sum()
        .sort_values(ascending=False)
        .head(5)
        .sort_values()
        .reset_index()
    )

    def netflix_title_group(value: object) -> str | None:
        text = str(value).strip() if pd.notna(value) else ""
        if not text or text.startswith(":"):
            return None
        if ":" in text:
            text = text.split(":", 1)[0].strip()
        return text or None

    netflix["title_group"] = netflix["title"].map(netflix_title_group)
    top_netflix_titles = (
        netflix.dropna(subset=["title_group"])
        .groupby("title_group")
        .size()
        .sort_values(ascending=False)
        .head(5)
        .sort_values()
        .reset_index(name="watch_count")
    )

    prime["title_group"] = (
        prime["series_title"]
        .fillna("")
        .astype(str)
        .str.strip()
        .where(
            prime["series_title"].fillna("").astype(str).str.strip().ne(""),
            prime["movie_title"].fillna("").astype(str).str.strip(),
        )
    )
    prime["title_group"] = prime["title_group"].where(
        prime["title_group"].ne(""),
        prime["title"].fillna("").astype(str).str.strip(),
    )
    top_prime_titles = (
        prime[prime["title_group"].ne("")]
        .groupby("title_group")
        .size()
        .sort_values(ascending=False)
        .head(5)
        .sort_values()
        .reset_index(name="watch_count")
    )

    long_form_monthly = combined.copy()
    long_form_monthly["month"] = long_form_monthly["fine_date"].dt.to_period("M").dt.to_timestamp()
    long_form_monthly = (
        long_form_monthly.groupby("month")[["netflix_daily_count", "prime_video_daily_count", "netflix_prime_daily_count"]]
        .sum()
        .reset_index()
    )
    netflix_title_text = netflix["title"].fillna("").astype(str).str.strip()
    netflix_bad_title_mask = netflix_title_text.eq("") | netflix_title_text.str.startswith(":")
    title_quality = [
        {"label": "usable title", "value": int((~netflix_bad_title_mask).sum())},
        {"label": "missing or malformed", "value": int(netflix_bad_title_mask.sum())},
    ]
    record_types = prime["record_type"].fillna("unknown").value_counts().reset_index()
    record_types.columns = ["label", "value"]

    return {
        "youtube": {
            "actionCounts": [
                {"label": str(row["action"]), "value": int(row["count"])}
                for _, row in youtube["action"].value_counts().reset_index(name="count").iterrows()
            ],
            "targetKindCounts": [
                {"label": str(row["target_kind"]), "value": int(row["count"])}
                for _, row in youtube["target_kind"].value_counts().reset_index(name="count").iterrows()
            ],
            "monthly": [
                {
                    "month": str(row["month"].date()),
                    "watched": int(row["youtube_daily_watched_count"]),
                    "search": int(row["youtube_daily_search_count"]),
                    "estimatedWatchHours": finite(row["youtube_estimated_continuous_watch_hours"]),
                }
                for _, row in youtube_monthly.iterrows()
            ],
            "hourly": [
                {
                    "hour": int(row["hour"]),
                    "total": int(row["total"]),
                    "watched": int(row["watched"]),
                    "search": int(row["search"]),
                }
                for _, row in youtube_hourly.iterrows()
            ],
        },
        "spotify": {
            "monthly": [
                {"month": str(row["month"].date()), "hours": finite(row["hours"]), "streams": int(row["streams"])}
                for _, row in spotify_monthly.iterrows()
            ],
            "hourly": [
                {"hour": int(row["hour"]), "hours": finite(row["hours"]), "streams": int(row["streams"])}
                for _, row in spotify_hourly.iterrows()
            ],
            "topArtists": [
                {"label": str(row["artist_name"]), "value": finite(row["hours_played"])}
                for _, row in top_artists.iterrows()
            ],
            "topTracks": [
                {"label": str(row["track_artist_label"]), "value": finite(row["minutes_played"])}
                for _, row in top_tracks.iterrows()
            ],
        },
        "longForm": {
            "totals": [
                {"label": "Netflix", "value": int(combined["netflix_daily_count"].sum())},
                {"label": "Prime Video", "value": int(combined["prime_video_daily_count"].sum())},
            ],
            "monthly": [
                {
                    "month": str(row["month"].date()),
                    "netflix": int(row["netflix_daily_count"]),
                    "prime": int(row["prime_video_daily_count"]),
                    "total": int(row["netflix_prime_daily_count"]),
                }
                for _, row in long_form_monthly.iterrows()
            ],
            "titleQuality": title_quality,
            "recordTypes": [
                {"label": str(row["label"]), "value": int(row["value"])}
                for _, row in record_types.iterrows()
            ],
            "topNetflixTitles": [
                {"label": str(row["title_group"]), "value": int(row["watch_count"])}
                for _, row in top_netflix_titles.iterrows()
            ],
            "topPrimeTitles": [
                {"label": str(row["title_group"]), "value": int(row["watch_count"])}
                for _, row in top_prime_titles.iterrows()
            ],
        },
    }


def boxplot_rows(
    frame: pd.DataFrame,
    group_column: str,
    value_column: str,
    order: list[str],
    label_map: dict[str, str] | None = None,
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for group in order:
        values = frame.loc[frame[group_column] == group, value_column].dropna()
        if values.empty:
            continue
        active_values = values[values > 0]
        rows.append(
            {
                "label": label_map.get(group, group) if label_map else group,
                "min": finite(values.min()),
                "q1": finite(values.quantile(0.25)),
                "median": finite(values.median()),
                "q3": finite(values.quantile(0.75)),
                "max": finite(values.max()),
                "mean": finite(values.mean()),
                "activeMean": finite(active_values.mean()) if not active_values.empty else 0,
                "activeMedian": finite(active_values.median()) if not active_values.empty else 0,
                "activeCount": int((values > 0).sum()),
                "count": int(len(values)),
            }
        )
    return rows


def prepare_boxplots(combined: pd.DataFrame) -> dict[str, list[dict[str, object]]]:
    frame = combined.copy()
    frame["weekday"] = frame["fine_date"].dt.day_name()
    weekday_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    period_order = ["ordinary_term", "final_exam", "outside_calendar", "summer_work_period"]
    period_labels = {
        "ordinary_term": "Ordinary term",
        "final_exam": "Final exam",
        "outside_calendar": "Outside calendar",
        "summer_work_period": "Summer work",
    }

    return {
        "youtubeWeekday": boxplot_rows(frame, "weekday", "youtube_daily_watched_count", weekday_order),
        "spotifyWeekday": boxplot_rows(frame, "weekday", "spotify_daily_hours", weekday_order),
        "longFormWeekday": boxplot_rows(frame, "weekday", "netflix_prime_daily_count", weekday_order),
        "youtubePeriod": boxplot_rows(
            frame, "analysis_period", "youtube_daily_watched_count", period_order, period_labels
        ),
        "spotifyPeriod": boxplot_rows(
            frame, "analysis_period", "spotify_daily_hours", period_order, period_labels
        ),
        "longFormPeriod": boxplot_rows(
            frame, "analysis_period", "netflix_prime_daily_count", period_order, period_labels
        ),
        "platformDiversityPeriod": boxplot_rows(
            frame,
            "analysis_period",
            "daily_distinct_entertainment_platform_count",
            period_order,
            period_labels,
        ),
        "youtubeAfterPeriod": boxplot_rows(
            frame, "analysis_period", "youtube_after_2130_count", period_order, period_labels
        ),
        "spotifyAfterPeriod": boxplot_rows(
            frame, "analysis_period", "spotify_after_2130_hours", period_order, period_labels
        ),
    }


def finite(value: float) -> float:
    if value is None or not math.isfinite(float(value)):
        return 0.0
    return round(float(value), 6)


def hypothesis_results(combined: pd.DataFrame) -> list[dict[str, object]]:
    results: list[dict[str, object]] = []
    final_days = combined[combined["analysis_period"] == "final_exam"]
    ordinary_days = combined[combined["analysis_period"] == "ordinary_term"]
    active_long_form_days = combined[combined["netflix_prime_active_day"]]
    inactive_long_form_days = combined[~combined["netflix_prime_active_day"]]

    def decision(p_value: float) -> str:
        return "Reject H0" if p_value < ALPHA else "Do not reject H0"

    def add_mann_whitney(
        hypothesis: str,
        outcome: str,
        comparison: str,
        group_1: pd.Series,
        group_2: pd.Series,
        interpretation: str,
    ) -> None:
        result = stats.mannwhitneyu(group_1, group_2, alternative="less")
        results.append(
            {
                "hypothesis": hypothesis,
                "outcome": outcome,
                "test": "Mann-Whitney U",
                "alternative": "one-sided less",
                "comparison": comparison,
                "nGroup1": int(len(group_1)),
                "nGroup2": int(len(group_2)),
                "meanGroup1": finite(group_1.mean()),
                "meanGroup2": finite(group_2.mean()),
                "medianGroup1": finite(group_1.median()),
                "medianGroup2": finite(group_2.median()),
                "statistic": finite(result.statistic),
                "pValue": finite(result.pvalue),
                "alpha": ALPHA,
                "decision": decision(result.pvalue),
                "interpretation": interpretation,
            }
        )

    h1_metrics = [
        ("YouTube watched count", "youtube_daily_watched_count"),
        ("Spotify listening hours", "spotify_daily_hours"),
        ("Netflix viewing count", "netflix_daily_count"),
        ("Prime Video viewing count", "prime_video_daily_count"),
    ]
    for label, column in h1_metrics:
        add_mann_whitney(
            "H1 Entertainment usage during academic pressure",
            label,
            "final_exam < ordinary_term",
            final_days[column],
            ordinary_days[column],
            "Current basic result does not provide strong evidence that this platform is lower during finals."
            if column in {"youtube_daily_watched_count", "spotify_daily_hours", "netflix_daily_count", "prime_video_daily_count"}
            else "",
        )

    add_mann_whitney(
        "H2 Platform diversity during academic pressure",
        "Distinct active entertainment platforms",
        "final_exam < ordinary_term",
        final_days["daily_distinct_entertainment_platform_count"],
        ordinary_days["daily_distinct_entertainment_platform_count"],
        "Platform diversity is slightly lower in finals, but the current basic test does not reject H0.",
    )
    add_mann_whitney(
        "H3 Long-form streaming and YouTube activity",
        "YouTube watched count",
        "Netflix+Prime active days < inactive days",
        active_long_form_days["youtube_daily_watched_count"],
        inactive_long_form_days["youtube_daily_watched_count"],
        "The current basic test does not support lower YouTube activity on Netflix+Prime active days.",
    )

    spearman = stats.spearmanr(
        combined["spotify_daily_hours"],
        combined["youtube_daily_watched_count"],
        alternative="greater",
    )
    results.append(
        {
            "hypothesis": "H4 Spotify and YouTube co-usage",
            "outcome": "Spotify hours and YouTube watched count",
            "test": "Spearman correlation",
            "alternative": "one-sided greater",
            "comparison": "spotify_daily_hours positively associated with youtube_daily_watched_count",
            "nGroup1": int(len(combined)),
            "nGroup2": int(len(combined)),
            "meanGroup1": finite(combined["spotify_daily_hours"].mean()),
            "meanGroup2": finite(combined["youtube_daily_watched_count"].mean()),
            "medianGroup1": finite(combined["spotify_daily_hours"].median()),
            "medianGroup2": finite(combined["youtube_daily_watched_count"].median()),
            "statistic": finite(spearman.statistic),
            "pValue": finite(spearman.pvalue),
            "alpha": ALPHA,
            "decision": decision(spearman.pvalue),
            "interpretation": "The association is statistically detectable in this basic test, but the effect is weak.",
        }
    )

    add_mann_whitney(
        "H5 After-9:30 PM entertainment during finals",
        "YouTube after-21:30 activity share",
        "final_exam < ordinary_term",
        final_days["youtube_after_2130_share"],
        ordinary_days["youtube_after_2130_share"],
        "The YouTube late-evening share is lower during finals in the current basic test.",
    )
    add_mann_whitney(
        "H5 After-9:30 PM entertainment during finals",
        "Spotify after-21:30 listening-hour share",
        "final_exam < ordinary_term",
        final_days["spotify_after_2130_hour_share"],
        ordinary_days["spotify_after_2130_hour_share"],
        "The Spotify late-evening listening share is lower during finals in the current basic test.",
    )

    for result in results:
        if result["decision"] == "Reject H0" and result["hypothesis"].startswith("H1"):
            result["interpretation"] = "This platform is lower during finals in the current basic test."
    return results


def copy_eda_images() -> list[dict[str, object]]:
    plots: list[dict[str, object]] = []
    for group_id, (group_label, source_dir, target_dir) in IMAGE_FOLDERS.items():
        target_dir.mkdir(parents=True, exist_ok=True)
        for stale in target_dir.glob("*.png"):
            stale.unlink()
        for source_path in sorted(source_dir.glob("*.png")):
            target_path = target_dir / source_path.name
            shutil.copy2(source_path, target_path)
            title = source_path.stem.replace("_", " ").title()
            plots.append(
                {
                    "id": source_path.stem,
                    "file": source_path.name,
                    "title": title,
                    "group": group_id,
                    "platform": group_label,
                    "src": f"/eda-images/{group_id}/{source_path.name}",
                    "caption": PLOT_CAPTIONS.get(source_path.name, "EDA plot for the public project dataset."),
                    "curated": source_path.name in CURATED_PLOTS,
                }
            )
    return plots


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    IMAGE_DIR.mkdir(parents=True, exist_ok=True)
    data = read_platform_data()
    combined, common_start, common_end = prepare_combined_daily(data)
    plots = copy_eda_images()

    dataset_summaries = []
    for dataset in DATASETS:
        frame = data[dataset["id"]]
        dataset_summaries.append(
            {
                "id": dataset["id"],
                "name": dataset["name"],
                "role": dataset["role"],
                "rowCount": int(len(frame)),
                "dateStart": str(frame["fine_date"].min().date()),
                "dateEnd": str(frame["fine_date"].max().date()),
                "publicPath": dataset["publicPath"],
                "color": dataset["color"],
                "notes": dataset["notes"],
            }
        )

    active_days = [
        {
            "platform": "YouTube",
            "activeDays": int((combined["youtube_daily_total_count"] > 0).sum()),
            "color": "#5db5f0",
        },
        {
            "platform": "Spotify",
            "activeDays": int((combined["spotify_daily_stream_count"] > 0).sum()),
            "color": "#7dd7ba",
        },
        {
            "platform": "Netflix",
            "activeDays": int((combined["netflix_daily_count"] > 0).sum()),
            "color": "#d29355",
        },
        {
            "platform": "Prime Video",
            "activeDays": int((combined["prime_video_daily_count"] > 0).sum()),
            "color": "#f0c96a",
        },
    ]

    monthly = combined.copy()
    monthly["month"] = monthly["fine_date"].dt.to_period("M").dt.to_timestamp()
    monthly = (
        monthly.groupby("month")[
            ["youtube_daily_watched_count", "spotify_daily_hours", "netflix_prime_daily_count"]
        ]
        .sum()
        .reset_index()
    )

    period_order = ["ordinary_term", "final_exam", "outside_calendar", "summer_work_period"]
    relative_columns = [
        "youtube_daily_watched_count",
        "spotify_daily_hours",
        "netflix_prime_daily_count",
        "daily_distinct_entertainment_platform_count",
    ]
    relative_labels = {
        "youtube_daily_watched_count": "YT watch",
        "spotify_daily_hours": "Spotify hrs",
        "netflix_prime_daily_count": "N+Prime",
        "daily_distinct_entertainment_platform_count": "Platforms",
    }
    period_means = combined.groupby("analysis_period")[relative_columns].mean().reindex(period_order)
    relative_rows = []
    for period, row in period_means.iterrows():
        for column in relative_columns:
            overall = combined[column].mean()
            relative_rows.append(
                {
                    "period": period,
                    "metric": relative_labels[column],
                    "value": finite(row[column] / overall if overall else 0),
                }
            )

    correlation_columns = [
        "youtube_daily_watched_count",
        "youtube_daily_search_count",
        "spotify_daily_hours",
        "spotify_daily_stream_count",
        "netflix_prime_daily_count",
        "daily_distinct_entertainment_platform_count",
        "youtube_after_2130_count",
        "spotify_after_2130_hours",
    ]
    correlation_labels = [
        "YT watch",
        "YouTube search",
        "Spotify hrs",
        "Spotify streams",
        "N+Prime",
        "Platforms",
        "YT 21:30",
        "Spotify 21:30",
    ]
    correlation = combined[correlation_columns].corr(method="spearman").fillna(0)

    project_summary = {
        "title": "Entertainment Behavior Under Academic Pressure",
        "subtitle": "A public data story from YouTube, Spotify, Netflix, Prime Video, and the academic calendar.",
        "commonDateRange": {
            "start": str(common_start.date()),
            "end": str(common_end.date()),
            "days": int(len(combined)),
        },
        "datasets": dataset_summaries,
        "edaPlots": plots,
        "hypothesisResults": hypothesis_results(combined),
        "roadmap": [
            "Polish formal hypothesis-test interpretation for the report.",
            "Add multiple-testing correction only if the project needs a stricter statistical layer.",
            "Add machine-learning cards later only when a real model exists.",
        ],
    }

    chart_series = {
        "coverage": [
            {
                "platform": item["name"],
                "start": item["dateStart"],
                "end": item["dateEnd"],
                "color": item["color"],
            }
            for item in dataset_summaries
        ],
        "activeDays": active_days,
        "monthlyTrends": [
            {
                "month": str(row["month"].date()),
                "youtubeWatched": int(row["youtube_daily_watched_count"]),
                "spotifyHours": finite(row["spotify_daily_hours"]),
                "netflixPrimeCount": int(row["netflix_prime_daily_count"]),
            }
            for _, row in monthly.iterrows()
        ],
        "relativeActivity": relative_rows,
        "periodCounts": [
            {"period": period, "days": int(count)}
            for period, count in combined["analysis_period"].value_counts().reindex(period_order).items()
        ],
        "correlation": {
            "labels": correlation_labels,
            "matrix": correlation.round(3).values.tolist(),
        },
        "dailyPanel": [
            {
                "date": str(row["fine_date"].date()),
                "analysisPeriod": row["analysis_period"],
                "youtubeWatched": int(row["youtube_daily_watched_count"]),
                "youtubeSearch": int(row["youtube_daily_search_count"]),
                "spotifyHours": finite(row["spotify_daily_hours"]),
                "spotifyStreams": int(row["spotify_daily_stream_count"]),
                "netflixPrimeCount": int(row["netflix_prime_daily_count"]),
                "platformDiversity": int(row["daily_distinct_entertainment_platform_count"]),
                "youtubeAfter2130Share": finite(row["youtube_after_2130_share"]),
                "spotifyAfter2130Share": finite(row["spotify_after_2130_hour_share"]),
                "youtubeEstimatedWatchMinutes": finite(row["youtube_estimated_continuous_watch_minutes"]),
            }
            for _, row in combined.iterrows()
        ],
        "hourlyActivity": prepare_hourly_activity(data),
        "platformEda": prepare_platform_eda(data, combined),
        "boxplots": prepare_boxplots(combined),
    }

    (DATA_DIR / "project-summary.json").write_text(json.dumps(project_summary, indent=2))
    (DATA_DIR / "chart-series.json").write_text(json.dumps(chart_series, indent=2))

    assert str(common_start.date()) == "2022-04-17"
    assert str(common_end.date()) == "2026-03-10"
    assert len(combined) == 1424
    public_summary_text = (DATA_DIR / "project-summary.json").read_text()
    blocked_tokens = ("LO" + "CAL", "data_" + "local", "/Us" + "ers/")
    assert not any(token in public_summary_text for token in blocked_tokens)

    print(f"Wrote {DATA_DIR / 'project-summary.json'}")
    print(f"Wrote {DATA_DIR / 'chart-series.json'}")
    print(f"Copied {len(plots)} EDA images")


if __name__ == "__main__":
    main()
