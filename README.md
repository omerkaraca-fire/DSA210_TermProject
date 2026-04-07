# DSA210_TermProject
This repository contains the term project for the course DSA210.
Author - Nihat Ömer Karaca e-mail: omer.karaca@sabanciuniv.edu or nihatomer.karaca@gmail.com

As an undergraduate student, I have been curious about how academic pressure shapes my daily digital behavior. During exam weeks, project deadlines, and finals, the way I use entertainment, social media, and AI tools seems to change, but I want to test that idea with data rather than intuition. For this reason, my project will study my cross-platform digital behavior under academic pressure by combining personal platform exports with an academic calendar that labels exam, project, final, and baseline periods with their cross correlations as well.

The data will come from my own account archives and activity exports: Spotify Extended Streaming History, YouTube and Google Takeout activity, Instagram activity export, Twitter archive, Netflix viewing history, Prime Video watch history, and ChatGPT export data. The repository currently contains approximately 178,438 Spotify stream rows, 34,317 YouTube activity rows, 69,513 Instagram events, 40,839 ChatGPT messages, 2,493 Netflix viewing-history rows, 719 Prime Video watch-history rows, and Twitter data including 664 tweets and 4,540 likes. I will collect these data through the platforms’ export tools (usually they are provided in their website platforms settings section.) and enrich them by merging them into a daily analysis table together with academic-period labels. Sidenote, the data itself is extremely detailed and confusing and would take time too explain it, and requires time to understand the core principles from the raw to processed data then to the EDA and hypothesis testing.

The project will group platforms into entertainment (Spotify, YouTube, Netflix, Prime Video), social (Instagram, Twitter), and AI or study-adjacent usage (ChatGPT). Because these platforms do not provide the same type of time information, I will distinguish between exact duration, estimated active usage, and activity counts instead of treating everything as identical screen time so any assumption from the raw information will be explained how it is done and how could have been better. After preprocessing and exploratory data analysis, I plan to test whether entertainment usage changes during academic-pressure periods, whether ChatGPT usage increases during those periods (I think that with recent changes normal chat usages (except the holiday, where i dont have to do anything with my life) increased), and whether cross-platform substitution or co-usage patterns appear.

## Repository Structure

The structure below reflects the current GitHub-facing repository layout.

```text
DSA210_TermProject/
├── DataScripts/
│   └── scripts/
│       ├── netflix/
│       └── youtube/
├── Reports/
│   ├── .gitignore
│   └── proposal.pdf
├── data_github/
│   ├── academical_calendar/
│   ├── netflix_public/
│   └── youtube_public/
├── .gitignore
├── LICENSE
├── ProjectRequirements.txt
└── README.md
```
