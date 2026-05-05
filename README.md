# DSA210_TermProject

This repository contains my term project for the course DSA210.


[DSA 210 Term Project](https://dsa-210-term-project-ten.vercel.app/)


If it does not work try this : https://dsa-210-term-project-ten.vercel.app



Author - Nihat Ömer Karaca  
E-mail - omer.karaca@sabanciuniv.edu or nihatomer.karaca@gmail.com

## Introduction

This project studies how my entertainment behavior changes under academic pressure. I started from the question of whether the platforms I use in daily life change during finals, midterms, and ordinary term days.

At first, I considered several personal data exports such as ChatGPT, Instagram, Netflix, Spotify, Twitter, and YouTube. After checking the project scope and privacy risks, I decided to exclude Instagram and Twitter because they would increase the complexity too much. I also postponed ChatGPT because it is a different domain and would need heavier privacy and parsing decisions.

The current public version focuses on YouTube, Spotify, Netflix, Prime Video, and the academic calendar. YouTube represents short-form and mixed video behavior, Spotify represents music listening duration, and Netflix + Prime Video represent long-form streaming. The academic calendar is used as a label source, not as a behavioral dataset.

## Project Website

The interactive website is inside `Vercel_Data_Visualisation/`.

Live website: [https://dsa-210-term-project-ten.vercel.app/](https://dsa-210-term-project-ten.vercel.app/)

For Vercel deployment from GitHub, import this repository and set the project root directory to `Vercel_Data_Visualisation`. Vercel should detect the Next.js app from that folder. Use the default install command and build command:

- Install command: `npm install`
- Build command: `npm run build`
- Output directory: leave as Vercel default for Next.js
- Environment variables: none required for the current version

## Raw Data / Public Data

The private raw exports were not equally clean or equally easy to use. Some platforms gave structured JSON or CSV files, while others needed more careful parsing and privacy handling. This README documents the public prepared data and the general cleaning logic, not private local raw folders.

| Dataset | Public output | Current public size | Date range | Notes |
|---|---|---:|---|---|
| YouTube | `data_github/youtube_public/` | 34,317 activity rows and 22 subscription rows | 2022-04-17 to 2026-03-15 | Google Takeout activity converted into public activity and subscription tables. |
| Spotify | `data_github/spotify_public/` | 178,202 streaming rows | 2019-07-27 to 2026-03-14 | Music-focused streaming history with timestamps and listening duration. |
| Netflix | `data_github/netflix_public/` | 2,493 viewing rows | 2020-02-25 to 2026-03-10 | Viewing-history data kept at row level with titles visible. |
| Prime Video | `data_github/prime_video_public/` | 719 watch-history rows | 2022-03-30 to 2026-03-19 | Watch-history data parsed into movie and episode records with titles visible. |
| Academic calendar | `data_github/academical_calendar/` | Calendar labels | 2021-2022 to 2025-2026 | Used as the label source for ordinary term and final-exam periods. |

## Methodology

The project uses the day as the main unit of analysis because all public datasets can be joined by `fine_date`. This makes it possible to compare platforms even though they measure behavior differently. Spotify has duration, YouTube has timestamped activity events, and Netflix and Prime Video mainly provide viewing records.

Each platform was first cleaned and converted into a public analysis-ready table. The platform scripts follow the same general flow: raw export to processed data, processed data to shared `fine_*` fields, and then a reduced public dataset under `data_github/`. Private identifiers and local paths were masked or removed before public release. Timestamps were preserved where they were available.

For EDA, I first inspected each dataset individually. YouTube EDA focused on action types, monthly activity, time of day, weekday behavior, and a conservative estimated watch-time proxy. Spotify EDA focused on monthly listening, hourly listening, top artists/tracks, and weekday behavior. Netflix and Prime Video EDA stayed separate in the public data but were also grouped as long-form streaming for analysis.

After the individual EDA, I built a combined daily panel for the common four-platform date window: 2022-04-17 to 2026-03-10. This panel has 1,424 daily rows. Missing platform rows on a date were treated as zero activity for that platform after aggregation. Netflix and Prime Video were combined only in the EDA and testing layer as long-form streaming, not as a separate public release file.

The hypothesis set was chosen after seeing which variables were clean enough to compare across platforms. I focused on academic pressure, platform diversity, same-day cross-platform behavior, and after-21:30 entertainment activity. Add/drop was not kept as a separate formal test group because it was not central enough for this version.

## Visualization

The EDA is presented in two ways:

- Notebook-generated PNG plots are kept for traceability and presentation reuse.
- The `Vercel_Data_Visualisation/` website rebuilds the main story with interactive SVG charts, hover tooltips, zoomable chart cards, an EDA appendix, and hypothesis result cards.

The website follows the same project logic as this README: public datasets, cleaning decisions, EDA, hypothesis testing, and current basic results.

## Hypothesis Test

The formal tests use daily variables from the combined public-data panel. The Mann-Whitney U test is used for the group comparisons because the daily activity variables are skewed and zero-heavy. Therefore, **a rank-based non-parametric test is more suitable** than assuming normally distributed data. Same-day Spotify and YouTube co-usage uses a one-sided Spearman correlation because it checks whether two variables move together monotonically without requiring a linear relationship.

The current version uses raw p-values with `alpha = 0.05`, so the results should be interpreted cautiously because multiple tests are being run.

| Hypothesis | H0 | H1 | Variables | Method |
|---|---|---|---|---|
| Entertainment usage during academic pressure | Platform activity does not differ between final-exam days and ordinary-term days. | Final-exam days have lower platform activity. | YouTube watched count, Spotify hours, Netflix count, Prime Video count | One-sided Mann-Whitney U, tested separately by platform |
| Platform diversity during academic pressure | Platform diversity does not differ between final-exam days and ordinary-term days. | Platform diversity is lower during finals. | Distinct active entertainment platforms per day | One-sided Mann-Whitney U |
| Netflix + Prime and YouTube activity | YouTube watched count does not differ between Netflix + Prime active and inactive days. | YouTube watched count is lower on Netflix + Prime active days. | Netflix count, Prime Video count, YouTube watched count | One-sided Mann-Whitney U |
| Spotify and YouTube co-usage | Spotify hours are not associated with YouTube watched count. | Spotify hours have a positive monotonic association with YouTube watched count. | Spotify hours, YouTube watched count | One-sided Spearman correlation |
| After-9:30 PM entertainment during finals | Late-evening entertainment share does not differ between final-exam days and ordinary-term days. | Late-evening share is lower during finals. | YouTube after-21:30 share, Spotify after-21:30 hour share | One-sided Mann-Whitney U, tested separately by platform |

Current basic results:

| Hypothesis | Outcome | Decision | Raw p-value | Short interpretation |
|---|---|---|---:|---|
| H1 | YouTube watched count | Do not reject H0 | 0.0908 | YouTube watched count was lower in finals on average, but not enough to reject H0 in this basic test. |
| H1 | Spotify listening hours | Do not reject H0 | 0.0697 | Spotify hours were lower in finals on average, but not enough to reject H0 in this basic test. |
| H1 | Netflix viewing count | Do not reject H0 | 0.8512 | Netflix did not support the expected lower-finals direction. |
| H1 | Prime Video viewing count | Do not reject H0 | 0.3890 | Prime Video did not provide enough evidence for lower finals usage. |
| H2 | Distinct active entertainment platforms | Do not reject H0 | 0.1305 | Platform diversity did not significantly decrease during finals. |
| H3 | YouTube watched count on Netflix + Prime active days | Do not reject H0 | 0.8731 | Long-form active days did not support lower YouTube watch activity. |
| H4 | Spotify hours and YouTube watched count | Reject H0 | 0.0002 | There is a statistically detectable but weak positive same-day association. |
| H5 | YouTube after-21:30 activity share | Reject H0 | 0.0059 | YouTube late-evening share was lower during finals in this basic test. |
| H5 | Spotify after-21:30 listening-hour share | Reject H0 | 0.0361 | Spotify late-evening listening share was lower during finals in this basic test. |

Main hypothesis-test interpretation:

- The p-values of the first three hypotheses are higher than `0.05`, so **there is no evidence to reject the null hypothesis** for those tests.
- For H4 and H5, the p-values are smaller than `0.05`, so the null hypotheses are **rejected in favor of the alternative hypothesis**.
- Not rejecting H1 might imply that I **do not significantly change my usage behavior during exam periods** and use the platforms similarly to ordinary periods.
- Not rejecting H3 might suggest that I **do not use YouTube significantly less when also using Netflix and Prime Video**.
- For H4, the result shows a **statistically significant positive** association between Spotify hours and YouTube watched count. However, the **relationship is weak**. The Spearman correlation coefficient is **rho = 0.0934, which is close to zero**. This means Spotify and YouTube usage tend to **increase together slightly**, but the relationship **should not be interpreted as strong**.
- For H5, the **late-evening entertainment** result suggests that Spotify and YouTube usage during final periods **was lower compared to ordinary days**.

## Machine Learning Extension

The machine learning part examines whether daily entertainment activity can predict period labels. Given the number of daily activities, I asked whether it would be possible to guess a day's class, where the class corresponds to ordinary term, final exam period, or summer work period.

Final exam period corresponds to the final exam period in the academic calendar. **Midterm dates are not separately labeled here; if they fall outside the final exam period, they remain inside the ordinary term class**, because each course distributes workload in different time periods. The summer work period corresponds to the summers where I worked as an intern in a local company in my hometown. The ordinary term class is the remaining labeled academic-term days.

As in the EDA and hypothesis testing parts, I used the Sabanci University academic calendar to determine these labels through `analysis_period`.

| Value | Meaning |
|---|---|
| `ordinary_term` | Regular academic term days |
| `final_exam` | Final exam period days |
| `summer_work_period` | Summer term/work period days |
| `outside_calendar` | Days outside the labeled academic calendar |

Classification happened in three ways:

| Classification Task | Classes Included | Full Dataset | Training Set | Test Set |
|---|---|---:|---:|---:|
| Final Exam vs Ordinary Term | `ordinary_term`, `final_exam` | 872 | 697 | 175 |
| Summer Work vs Ordinary Term | `ordinary_term`, `summer_work_period` | 979 | 783 | 196 |
| All Periods Classification | `ordinary_term`, `final_exam`, `summer_work_period` | 1,076 | 860 | 216 |

Common feature columns for final-exam ML and all-class ML:

| Feature Column |
|---|
| `youtube_daily_watched_count` |
| `youtube_daily_search_count` |
| `youtube_after_2130_count` |
| `spotify_daily_hours` |
| `spotify_daily_stream_count` |
| `spotify_daily_unique_tracks` |
| `spotify_after_2130_hours` |
| `netflix_daily_count` |
| `prime_video_daily_count` |
| `netflix_prime_daily_count` |
| `daily_distinct_entertainment_platform_count` |

Additional features for summer work period classification:

| Feature Column |
|---|
| `youtube_after_2130_share` |
| `spotify_after_2130_hour_share` |

Decision Tree validation splits:

| Classification Task | Decision Tree Training Subset | Decision Tree Validation Set |
|---|---:|---:|
| Final Exam vs Ordinary Term | 522 | 175 |
| Summer Work vs Ordinary Term | 587 | 196 |
| All Periods Classification | 645 | 215 |

The models used are Dummy Classifier, Logistic Regression, Decision Tree, XGBoost, Random Forest, and an Ensemble Model that soft-votes across the supervised models. K-Means is included as an unsupervised comparison, where clusters are mapped to labels after fitting.

Current ML summary:

| Classification Task | Dummy Macro F1 | Best Model | Best Model Macro F1 | Absolute Increase | Relative Improvement |
|---|---:|---|---:|---:|---:|
| Final Exam vs Ordinary Term | 47.13% | Ensemble Model | 51.85% | +4.72 percentage points | +10.01% |
| Summer Work vs Ordinary Term | 44.16% | XGBoost | 66.67% | +22.51 percentage points | +50.97% |
| All Periods: Ordinary vs Final vs Summer | 27.96% | Ensemble Model | 44.93% | +16.97 percentage points | +60.70% |

The separation hints that the summer work period pattern is easier to capture with the available features. The current feature set is not enough to strongly differentiate the final exam period and ordinary term. This can happen either because final exam behavior is not very different from ordinary term behavior, or because important social-media signals are still excluded from the current feature set.

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
├── EDA/
├── Hypothesis_Testing/
├── MachineLearning/
├── Reports/
│   ├── .gitignore
│   ├── Report_EDA_Hypothesis.pdf
│   └── proposal.pdf
├── Vercel_Data_Visualisation/
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
