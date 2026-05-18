# DSA210_TermProject

This repository contains my term project for the course DSA210.

My project website for better visualization:
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

## Python Environment

Python dependencies for the notebooks and data-processing scripts are listed in `requirements.txt`. I recommend using a virtual environment before running the notebooks or scripts.

macOS / Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m ipykernel install --user --name dsa210-term-project --display-name "DSA210 Term Project"
```

Windows PowerShell:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m ipykernel install --user --name dsa210-term-project --display-name "DSA210 Term Project"
```

The website has its own JavaScript dependencies inside `Vercel_Data_Visualisation/package.json`, so the website should be installed separately with `npm install` inside that folder.

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
| Long-form streaming and YouTube activity | YouTube watched count does not differ between Netflix + Prime active and inactive days. | YouTube watched count is lower on Netflix + Prime active days. | Netflix count, Prime Video count, YouTube watched count | One-sided Mann-Whitney U |
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
| H3 | YouTube watched count on long-form active days | Do not reject H0 | 0.8731 | The direction was opposite to H1: mean YouTube watched count was higher on Netflix + Prime active days, so the lower-YouTube alternative could not be rejected. |
| H4 | Spotify hours and YouTube watched count | Reject H0 | 0.0002 | Statistically detectable but practically very weak positive same-day association (`rho = 0.0934`). |
| H5 | YouTube after-21:30 activity share | Reject H0 | 0.0059 | YouTube late-evening share was lower during finals in this basic test. |
| H5 | Spotify after-21:30 listening-hour share | Reject H0 | 0.0342 | Spotify late-evening listening share was lower during finals in this basic test. |

Main hypothesis-test interpretation:

- The p-values of the first three hypotheses are higher than `0.05`, so **there is no evidence to reject the null hypothesis** for those tests.
- For H4 and H5, the p-values are smaller than `0.05`, so the null hypotheses are **rejected in favor of the alternative hypothesis**.
- Not rejecting H1 might imply that I **do not significantly change my usage behavior during exam periods** and use the platforms similarly to ordinary periods.
- Not rejecting H3 is especially clear because the observed direction was opposite to the alternative: mean YouTube watched count was higher on Netflix + Prime active days than inactive days.
- For H4, the result shows a **statistically significant positive** association between Spotify hours and YouTube watched count. However, the **relationship is very weak**. The Spearman correlation coefficient is **rho = 0.0934, which is close to zero**. This means Spotify and YouTube usage tend to **increase together slightly**, but the relationship **should not be interpreted as strong**; the small p-value is helped by the large daily sample size.
- For H5, the **YouTube after-21:30 share** result is clearly rejected at `p = 0.0059`, suggesting lower late-evening YouTube share during finals.
- For H5, the **Spotify after-21:30 listening-hour share** result is also rejected at `p = 0.0342`, but it is weaker and closer to the `0.05` threshold.

## Machine Learning Extension

The current machine learning notebook is `MachineLearning/machinelearning.ipynb`. It examines whether daily entertainment activity can predict academic-period labels. Given the number of daily activities, I asked whether it would be possible to guess a day's class, where the class corresponds to ordinary term, final exam period, or summer work period.

Final exam period corresponds to the final exam period in the academic calendar. **Midterm dates are not separately labeled here; if they fall outside the final exam period, they remain inside the ordinary term class**, because each course distributes workload in different time periods. The summer work period corresponds to the summers where I worked as an intern in a local company in my hometown. The ordinary term class is the remaining labeled academic-term days.

As in the EDA and hypothesis testing parts, I used the Sabanci University academic calendar to determine these labels through `analysis_period`.

| Value | Meaning |
|---|---|
| `ordinary_term` | Regular academic term days |
| `final_exam` | Final exam period days |
| `summer_work_period` | Summer term/work period days |
| `outside_calendar` | Days outside the labeled academic calendar |

The newest ML outputs are saved under `MachineLearning/results2/`. The older `MachineLearning/oldresults/` folder is kept only for reference and should not be treated as the latest result source.

Classification happened in three ways:

| Classification Task | Classes Included | Full Class Balance | Full Dataset | Training Set | Test Set |
|---|---|---|---:|---:|---:|
| Final Exam vs Ordinary Term | `ordinary_term`, `final_exam` | 775 ordinary, 97 final (11.1% final) | 872 | 697 | 175 |
| Summer Work vs Ordinary Term | `ordinary_term`, `summer_work_period` | 775 ordinary, 204 summer (20.8% summer) | 979 | 783 | 196 |
| All Periods Classification | `ordinary_term`, `final_exam`, `summer_work_period` | 775 ordinary, 97 final, 204 summer | 1,076 | 860 | 216 |

The final-exam task is especially imbalanced. In the held-out test set, there are 156 ordinary-term days and only 19 final-exam days. This explains why accuracy and macro F1 can move in opposite directions: the dummy classifier reaches 89.14% accuracy by predicting the majority class, but its macro F1 is only 47.13%. XGBoost and the ensemble reduce accuracy to 84.00% while increasing macro F1 to 51.85%, because they trade some majority-class correctness for a small amount of final-exam recall.

Feature columns for final-exam ML and all-class ML:

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

The summer work period classification uses the same feature columns above, plus two additional late-evening share features:

| Feature Column |
|---|
| `youtube_after_2130_share` |
| `spotify_after_2130_hour_share` |

Because the summer work task uses these two additional share features, the three classification tasks are not a perfectly identical feature-set comparison. The summer result is still useful, but part of its stronger macro-F1 score may come from having this richer feature set. If the feature set were reduced to the same 11 columns for every task, the summer score could change. Therefore, the ML conclusion should be read as: the current task-specific feature set captures summer work behavior more clearly than final exam behavior, not as a strict apples-to-apples proof that summer behavior is always easier to classify.

The supervised models use an 80/20 train/test split with stratification. After the split, parameter tuning is done with `GridSearchCV` and 5-fold `StratifiedKFold` cross-validation on the training set only. This keeps the test set separate until final evaluation.

| Classification Task | Train/Test Split | Cross-Validation | Tuning Criterion |
|---|---|---|---|
| Final Exam vs Ordinary Term | 80/20 stratified split | 5-fold StratifiedKFold on training data | Macro F1 |
| Summer Work vs Ordinary Term | 80/20 stratified split | 5-fold StratifiedKFold on training data | Macro F1 |
| All Periods Classification | 80/20 stratified split | 5-fold StratifiedKFold on training data | Macro F1 |

The models used are Dummy Classifier, Logistic Regression, Decision Tree, DBSCAN, XGBoost, Random Forest, and a Voting Ensemble. DBSCAN is included as an unsupervised reference-only comparison, where clusters are mapped to labels after fitting, so it should not be read as a directly comparable supervised classifier.

The supervised models are tuned with GridSearchCV on the training set, while the held-out test set is used only for final evaluation. Logistic Regression tunes regularization choices, Decision Tree tunes tree-shape and class-weight settings, XGBoost tunes boosting/tree settings where GridSearchCV is used, Random Forest tunes forest and tree-size settings, and the ensemble tunes voting type and model weights. DBSCAN tunes `eps` and `min_samples` using silhouette score.

| Classification Task | Models Used Inside Ensemble |
|---|---|
| Final Exam vs Ordinary Term | Logistic Regression, tuned Decision Tree, XGBoost, Random Forest |
| Summer Work vs Ordinary Term | Logistic Regression, tuned Decision Tree, XGBoost, Random Forest |
| All Periods Classification | Logistic Regression, tuned Decision Tree, XGBoost, Random Forest |

Current ML summary:

| Classification Task | Dummy Macro F1 | Best Model | Best Model Macro F1 | Absolute Increase | Relative Improvement |
|---|---:|---|---:|---:|---:|
| Final Exam vs Ordinary Term | 47.13% | XGBoost / Ensemble Model | 51.85% | +4.72 percentage points | +10.01% |
| Summer Work vs Ordinary Term | 44.16% | Ensemble Model | 68.59% | +24.43 percentage points | +55.32% |
| All Periods: Ordinary vs Final vs Summer | 27.96% | XGBoost | 44.52% | +16.56 percentage points | +59.25% |

For final exam period versus ordinary term, the tuned models improved only slightly over the dummy baseline. This suggests that the current features provide limited predictive signal for distinguishing final exam days from ordinary term days.

For summer work period versus ordinary term, the tuned ensemble model improved much more clearly over the dummy baseline. This suggests that the task-specific available features capture summer work behavior more clearly than final exam behavior.

The separation hints that the summer work period pattern is easier to capture with the current task-specific features. However, because the summer task includes the two additional late-evening share columns, the comparison is not fully apples-to-apples. The final-exam feature set is not enough to strongly differentiate the final exam period and ordinary term. This can happen either because final exam behavior is not very different from ordinary term behavior, or because important social-media signals are still excluded from the current feature set.

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
│   ├── machinelearning.ipynb
│   ├── machinelearningOLD_FOR_REFERENCE.ipynb
│   ├── oldresults/
│   │   ├── ACADEMICAL_PERIOD/
│   │   ├── All_CLASSIFICATION/
│   │   └── SUMMER_WORK_PERIOD/
│   └── results2/
│       ├── ACADEMICAL_PERIOD/
│       ├── All_CLASSIFICATION/
│       └── SUMMER_WORK_PERIOD/
├── Reports/
│   ├── .gitignore
│   ├── Final_Report.tex
│   ├── Final_Report.pdf
│   ├── Report_EDA_Hypothesis.tex
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
├── requirements.txt
└── README.md
```
