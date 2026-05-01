import { EdaGallery } from "@/components/EdaGallery";
import {
  MLAllModelMatrices,
  MLBestModels,
  MLMetricComparisonChart,
} from "@/components/MachineLearningCharts";
import { Reveal } from "@/components/Reveal";
import { DatasetCards } from "@/components/StatCards";
import {
  ActiveDaysChart,
  CoverageTimeline,
  DailyDistributionSmallMultiples,
  HourlyActivityChart,
  HypothesisMatrix,
  MonthlyTrendChart,
  RelativeActivityChart,
} from "@/components/Charts";
import {
  AnimatedPipeline,
  InteractiveBarChart,
  InteractiveBoxPlot,
  InteractiveDailyScatter,
  InteractiveHeatmap,
  InteractiveMonthlyLines,
  SparseActivityChart,
} from "@/components/StoryCharts";
import { ZoomableChart } from "@/components/ZoomableChart";
import {
  appendixPlots,
  chartSeries,
  formatNumber,
  formatPValue,
  machineLearningResults,
  projectSummary,
} from "@/lib/data";

const metricCards = [
  { value: projectSummary.commonDateRange.days.toLocaleString("en-US"), label: "daily rows in the shared analysis window" },
  { value: projectSummary.datasets.length.toString(), label: "public behavior datasets" },
  { value: appendixPlots.length.toString(), label: "appendix figures" },
  { value: projectSummary.hypothesisResults.length.toString(), label: "basic result rows" },
];

const rawDatasetNotes = [
  {
    title: "YouTube",
    raw: "Google Takeout activity export with watch/search-style events and timestamps.",
    kept: "Action type, target kind, masked channel references, timestamps, and daily activity fields.",
    excluded: "Real channel names and direct source identifiers were removed or masked.",
  },
  {
    title: "Spotify",
    raw: "Structured streaming-history JSON with exact timestamps and listening duration.",
    kept: "Track, artist, album, timestamp, milliseconds played, minutes played, and hours played.",
    excluded: "Account identifiers, IP-like fields, and raw source-file identifiers were removed.",
  },
  {
    title: "Netflix",
    raw: "Viewing-history CSV with title and date-level viewing records.",
    kept: "Original title string and viewing date at row level.",
    excluded: "No forced show/season/episode split because some Netflix titles are too inconsistent to parse safely.",
  },
  {
    title: "Prime Video",
    raw: "Watch-history export parsed into movie and episode records.",
    kept: "Title, record type, series/movie fields where available, and date-level watch records.",
    excluded: "Raw parse issues and local source details stay out of the public browser app.",
  },
];

const scriptNotes = [
  "Platform scripts normalize raw exports into processed row-level tables.",
  "fine_* builders create shared date, platform, source, and record-id fields.",
  "Public builders reduce the schema and mask source/account identifiers.",
  "EDA notebooks aggregate public rows to daily and monthly variables.",
  "The web app uses compact aggregate JSON and copied plot images, not full raw CSVs.",
];

const hypotheses = [
  {
    id: "H1",
    title: "Entertainment usage during academic pressure",
    h0: "Platform activity does not differ between final-exam days and ordinary-term days.",
    h1: "Final-exam days have lower platform activity.",
    method: "One-sided Mann-Whitney U",
    formula: "H1: X_final < X_ordinary",
  },
  {
    id: "H2",
    title: "Platform diversity during academic pressure",
    h0: "Platform diversity does not differ between final-exam days and ordinary-term days.",
    h1: "Platform diversity is lower during finals.",
    method: "One-sided Mann-Whitney U",
    formula: "D = count(active platforms per day)",
  },
  {
    id: "H3",
    title: "Netflix + Prime and YouTube activity",
    h0: "YouTube watched count does not differ between Netflix + Prime active and inactive days.",
    h1: "YouTube watched count is lower on Netflix + Prime active days.",
    method: "One-sided Mann-Whitney U",
    formula: "YouTube | long-form active < YouTube | inactive",
  },
  {
    id: "H4",
    title: "Spotify and YouTube co-usage",
    h0: "Spotify hours are not associated with YouTube watched count.",
    h1: "Spotify hours are positively associated with YouTube watched count.",
    method: "One-sided Spearman correlation",
    formula: "rho_s = corr(rank(Spotify), rank(YouTube))",
  },
  {
    id: "H5",
    title: "After-9:30 PM entertainment during finals",
    h0: "Late-evening entertainment share does not differ between final-exam days and ordinary-term days.",
    h1: "Late-evening share is lower during finals.",
    method: "One-sided Mann-Whitney U",
    formula: "share_after_2130 = after_2130 / daily_total",
  },
];

const chartDescriptions = {
  youtubeAction: "Uses YouTube action counts to show whether the dataset is mostly watch activity, search activity, or other actions.",
  youtubeMonthly: "Uses monthly watched and search counts to show how YouTube activity changes over time.",
  youtubeEstimatedWatch: "Uses gaps between consecutive watched-video timestamps to estimate rough monthly watch time.",
  youtubeHourly: "Uses YouTube timestamps converted to Istanbul time to show which hours have more YouTube activity.",
  youtubeWeekday: "Uses daily watched counts grouped by weekday to inspect whether YouTube use changes by day of week.",
  spotifyMonthly: "Uses Spotify monthly listening hours and stream counts to show long-term listening patterns.",
  spotifyHourly: "Uses Spotify timestamps and hours played to show which hours have more listening activity.",
  spotifyArtists: "Uses total Spotify hours per artist to show the most repeated artists.",
  spotifyTracks: "Uses total listening minutes per track to show the most repeated individual songs.",
  spotifyWeekday: "Uses daily Spotify hours grouped by weekday to inspect weekday differences.",
  longFormTotals: "Uses Netflix and Prime Video row counts to compare their total contribution.",
  longFormMonthly: "Uses monthly Netflix, Prime Video, and combined counts to show long-form viewing over time.",
  primeRecordTypes: "Uses Prime Video record type to show whether the records are mostly episodes or movies.",
  netflixTitleQuality: "Uses Netflix title quality checks to show usable titles versus missing or malformed title rows.",
  netflixTopTitles: "Uses grouped Netflix titles to show the most repeated Netflix series or title groups.",
  primeTopTitles: "Uses Prime Video series and movie titles to show the most repeated Prime Video titles.",
  longFormWeekday: "Uses active Netflix + Prime days only, excluding zero days, to show which weekdays had actual long-form use.",
  spotifyYoutubeScatter: "Uses daily Spotify hours and YouTube watched count to inspect same-day co-usage.",
  longFormYoutubeScatter: "Uses daily Netflix + Prime count and YouTube watched count to inspect whether long-form activity relates to YouTube activity.",
  heatmap: "Uses daily platform variables to show which variables move together more strongly.",
  youtubePeriod: "Uses YouTube watched count grouped by academic period to compare ordinary days, finals, and other periods.",
  spotifyPeriod: "Uses Spotify daily hours grouped by academic period to compare listening across periods.",
  longFormPeriod: "Uses active long-form days grouped by academic period, excluding zero days for readability.",
  platformDiversityPeriod: "Uses the number of active platforms per day to show whether platform variety changes by period.",
  youtubeAfterPeriod: "Uses YouTube activity after 21:30 to inspect late-evening behavior across academic periods.",
  spotifyAfterPeriod: "Uses Spotify listening after 21:30 to inspect late-evening listening across academic periods.",
  coverage: "Uses each platform's date range to show the common window where all datasets overlap.",
  activeDays: "Uses daily activity flags to show how many days each platform appears in the common window.",
  monthlyTrends: "Uses monthly YouTube watched count, Spotify hours, and Netflix + Prime count as separate trend panels.",
  dailyDistribution: "Uses daily variables to show skew, zero-heavy behavior, and outliers.",
  relativeActivity: "Uses period averages divided by overall averages to compare platforms without mixing raw units.",
  hourlyCombined: "Uses YouTube and Spotify timestamps to compare time-of-day behavior in Istanbul time.",
};

export default function HomePage() {
  const eda = chartSeries.platformEda;

  return (
    <main className="page-shell warm-story">
      <section className="hero-grid flex items-center" id="project">
        <Reveal className="hero-intro-block relative z-10">
          <p className="eyebrow">DSA210 term project</p>
          <h1 className="hero-title">{projectSummary.title}</h1>
          <div className="project-intro">
            <p>
              Hello, my name is Nihat Ömer Karaca. I am a CS & IE double-major student studying at
              Sabancı University.
            </p>
            <p>
              For our DSA210 course project, we were supposed to select a dataset and implement what the
              course required. I started by thinking about my daily life and what I actually do during
              ordinary days, midterms, and finals.
            </p>
            <p>
              After brainstorming, I realized that I was spending a lot of time on some platforms, and that
              this might be affected by academic requirements such as finals and midterms. I also thought
              that the platforms I use, such as Spotify, streaming platforms, YouTube, and the academic
              calendar, might affect each other. Maybe they pave the way for each other, or maybe they create
              a blockade.
            </p>
            <p>
              Because of that, I downloaded and considered several datasets: ChatGPT, Instagram, Netflix,
              Spotify, Twitter, and YouTube. After careful consideration, I decided to exclude Instagram and
              Twitter because they would have increased the complexity of the project too much. I also
              postponed ChatGPT because it is a completely different domain and would need a heavier privacy
              and parsing process. So I stuck with YouTube, Spotify, Netflix, Prime Video, and the academic
              calendar.
            </p>
            <p>
              I also prefer looking at project content on a webpage rather than only inside notebook files.
              That is why I created this page as a public-facing explanation of the project. Webpage
              explanation will be filled later (TODO).
            </p>
            <div className="content-list" aria-label="Website content">
              <span>Raw and public datasets</span>
              <span>Processing scripts</span>
              <span>Individual EDA</span>
              <span>Combined EDA</span>
              <span>Hypotheses</span>
              <span>Current test results</span>
              <span>Notebook plot appendix</span>
            </div>
          </div>
          <div className="mt-8 flex flex-wrap gap-3">
            <a className="cta-link" href="#data">
              Data and scripts
            </a>
            <a className="cta-link" href="#eda">
              Interactive EDA
            </a>
            <a className="cta-link" href="#hypotheses">
              Hypothesis results
            </a>
          </div>
        </Reveal>
      </section>

      <section className="section-tight">
        <Reveal className="metric-strip">
          {metricCards.map((metric) => (
            <article className="metric-card" key={metric.label}>
              <strong>{metric.value}</strong>
              <span>{metric.label}</span>
            </article>
          ))}
        </Reveal>
      </section>

      <section className="section" id="data">
        <Reveal>
          <p className="eyebrow">Raw data and public outputs</p>
          <h2 className="section-title">Different exports, one daily frame.</h2>
          <p className="section-copy">
            The raw exports were not equally clean: some arrived as structured CSV/JSON, while others needed
            parsing and privacy decisions. The public version keeps only the fields needed for analysis and
            uses the day as the shared unit.
          </p>
        </Reveal>
        <Reveal delay={0.1}>
          <DatasetCards datasets={projectSummary.datasets} />
        </Reveal>
        <Reveal className="raw-note-grid" delay={0.15}>
          {rawDatasetNotes.map((item) => (
            <article className="raw-note-card" key={item.title}>
              <h3>{item.title}</h3>
              <p><strong>Raw shape:</strong> {item.raw}</p>
              <p><strong>Kept:</strong> {item.kept}</p>
              <p><strong>Excluded:</strong> {item.excluded}</p>
            </article>
          ))}
        </Reveal>
      </section>

      <section className="section" id="scripts">
        <div className="section-grid">
          <Reveal className="sticky-note">
            <p className="eyebrow">Processing scripts</p>
            <h2 className="section-title">From export to public analysis.</h2>
            <p className="section-copy">
              Each platform follows the same logic: normalize the raw export, create shared `fine_*` fields,
              reduce the public schema, then aggregate later for EDA and testing.
            </p>
            <div className="script-note-stack">
              {scriptNotes.map((note, index) => (
                <span key={note}>{index + 1}. {note}</span>
              ))}
            </div>
          </Reveal>
          <Reveal className="chart-panel" delay={0.1}>
            <ZoomableChart title="Processing pipeline">
              <AnimatedPipeline />
            </ZoomableChart>
          </Reveal>
        </div>
      </section>

      <section className="section" id="eda">
        <Reveal>
          <p className="eyebrow">Interactive EDA</p>
          <h2 className="section-title">Interactive exploratory analysis.</h2>
          <p className="section-copy">
            These charts are SVG-based and interactive. Hover bars, points, and cells to see values and
            highlight the element being inspected.
          </p>
        </Reveal>

        <div className="eda-story-stack">
          <Reveal className="platform-eda-block">
            <div className="platform-eda-copy">
              <p className="eyebrow">YouTube EDA</p>
              <h3>YouTube activity overview.</h3>
              <p>
                YouTube is mostly watch activity. The estimated watch-time line is a conservative proxy:
                it sums gaps of up to 60 minutes between consecutive watched-video timestamps.
              </p>
            </div>
            <div className="platform-eda-grid">
              <ZoomableChart title="YouTube activity by action" description={chartDescriptions.youtubeAction}>
                <InteractiveBarChart data={eda.youtube.actionCounts} title="YouTube activity by action" unit="rows" color="#d97b47" horizontal />
              </ZoomableChart>
              <ZoomableChart title="Monthly YouTube watched and search counts" description={chartDescriptions.youtubeMonthly}>
                <InteractiveMonthlyLines
                  data={eda.youtube.monthly}
                  title="Monthly YouTube watched and search counts"
                  series={[
                    { key: "watched", label: "Watched", color: "#e58d55", unit: "records" },
                    { key: "search", label: "Search", color: "#f2c078", unit: "records" },
                  ]}
                />
              </ZoomableChart>
              <ZoomableChart title="Estimated continuous YouTube watch time" description={chartDescriptions.youtubeEstimatedWatch}>
                <InteractiveMonthlyLines
                  data={eda.youtube.monthly}
                  title="Estimated continuous YouTube watch time"
                  series={[
                    { key: "estimatedWatchHours", label: "Estimated hours", color: "#9ed8b3", unit: "hours" },
                  ]}
                />
              </ZoomableChart>
              <ZoomableChart title="YouTube activity by hour" description={chartDescriptions.youtubeHourly}>
                <InteractiveBarChart data={eda.youtube.hourly.map((row) => ({ label: `${row.hour}:00`, value: row.total }))} title="YouTube activity by hour" unit="records" color="#f2a65a" />
              </ZoomableChart>
              <ZoomableChart title="YouTube watched count by weekday" description={chartDescriptions.youtubeWeekday}>
                <InteractiveBoxPlot data={chartSeries.boxplots.youtubeWeekday} title="YouTube watched count by weekday" unit="records" color="#e58d55" />
              </ZoomableChart>
            </div>
          </Reveal>

          <Reveal className="platform-eda-block">
            <div className="platform-eda-copy">
              <p className="eyebrow">Spotify EDA</p>
              <h3>Spotify listening overview.</h3>
              <p>The main EDA checks monthly listening, time of day, and artist concentration without using it as a final hypothesis directly.</p>
            </div>
            <div className="platform-eda-grid">
              <ZoomableChart title="Monthly Spotify listening" description={chartDescriptions.spotifyMonthly}>
                <InteractiveMonthlyLines
                  data={eda.spotify.monthly}
                  title="Monthly Spotify listening"
                  series={[
                    { key: "hours", label: "Hours", color: "#86b889", unit: "hours" },
                    { key: "streams", label: "Streams", color: "#ffd08a", unit: "streams" },
                  ]}
                />
              </ZoomableChart>
              <ZoomableChart title="Spotify listening by hour" description={chartDescriptions.spotifyHourly}>
                <InteractiveBarChart data={eda.spotify.hourly.map((row) => ({ label: `${row.hour}:00`, value: row.hours }))} title="Spotify listening by hour" unit="hours" color="#86b889" />
              </ZoomableChart>
              <ZoomableChart title="Top Spotify artists by listening hours" description={chartDescriptions.spotifyArtists}>
                <InteractiveBarChart data={eda.spotify.topArtists} title="Top Spotify artists by listening hours" unit="hours" color="#c9925a" horizontal />
              </ZoomableChart>
              <ZoomableChart title="Top Spotify tracks by listening minutes" description={chartDescriptions.spotifyTracks}>
                <InteractiveBarChart data={eda.spotify.topTracks} title="Top Spotify tracks by listening minutes" unit="minutes" color="#86b889" horizontal />
              </ZoomableChart>
              <ZoomableChart title="Spotify listening hours by weekday" description={chartDescriptions.spotifyWeekday}>
                <InteractiveBoxPlot data={chartSeries.boxplots.spotifyWeekday} title="Spotify listening hours by weekday" unit="hours" color="#86b889" />
              </ZoomableChart>
            </div>
          </Reveal>

          <Reveal className="platform-eda-block">
            <div className="platform-eda-copy">
              <p className="eyebrow">Netflix + Prime Video EDA</p>
              <h3>Long-form streaming overview.</h3>
              <p>
                Netflix and Prime stay separate public datasets, but the EDA groups them as long-form
                streaming. Because most days have zero long-form activity, active-day charts are clearer
                than standard boxplots for this part.
              </p>
              <p className="eda-explanation">
                Manual data check: in the common 1,424-day window, 1,160 days have zero Netflix + Prime
                records and only 264 days are active. Since at least 75% of each weekday group is zero,
                the standard boxplot has Q1 = median = Q3 = 0. The chart below excludes zero days so it
                shows which weekdays had actual long-form use. Top-title charts are also shown as EDA
                summaries; Netflix uses conservative title groups only for display, while the public file
                still keeps the original title text.
              </p>
            </div>
            <div className="platform-eda-grid">
              <ZoomableChart title="Long-form total count by platform" description={chartDescriptions.longFormTotals}>
                <InteractiveBarChart data={eda.longForm.totals} title="Long-form total count by platform" unit="records" color="#d78355" />
              </ZoomableChart>
              <ZoomableChart title="Monthly long-form streaming" description={chartDescriptions.longFormMonthly}>
                <InteractiveMonthlyLines
                  data={eda.longForm.monthly}
                  title="Monthly long-form streaming"
                  series={[
                    { key: "netflix", label: "Netflix", color: "#d78355", unit: "views" },
                    { key: "prime", label: "Prime Video", color: "#f2c078", unit: "views" },
                    { key: "total", label: "Netflix + Prime", color: "#9ed8b3", unit: "views" },
                  ]}
                />
              </ZoomableChart>
              <ZoomableChart title="Prime Video record type split" description={chartDescriptions.primeRecordTypes}>
                <InteractiveBarChart data={eda.longForm.recordTypes} title="Prime Video record type split" unit="records" color="#b86f4b" />
              </ZoomableChart>
              <ZoomableChart title="Netflix title quality" description={chartDescriptions.netflixTitleQuality}>
                <InteractiveBarChart data={eda.longForm.titleQuality} title="Netflix title quality" unit="records" color="#e0a15f" />
              </ZoomableChart>
              <ZoomableChart title="Top Netflix title groups" description={chartDescriptions.netflixTopTitles}>
                <InteractiveBarChart data={eda.longForm.topNetflixTitles} title="Top Netflix title groups" unit="views" color="#d78355" horizontal />
              </ZoomableChart>
              <ZoomableChart title="Top Prime Video titles" description={chartDescriptions.primeTopTitles}>
                <InteractiveBarChart data={eda.longForm.topPrimeTitles} title="Top Prime Video titles" unit="views" color="#f2c078" horizontal />
              </ZoomableChart>
              <ZoomableChart title="Long-form streaming by weekday" description={chartDescriptions.longFormWeekday}>
                <SparseActivityChart data={chartSeries.boxplots.longFormWeekday} title="Netflix + Prime active days by weekday" unit="records" color="#d78355" />
              </ZoomableChart>
            </div>
          </Reveal>

          <Reveal className="platform-eda-block">
            <div className="platform-eda-copy">
              <p className="eyebrow">Combined EDA</p>
              <h3>Combined daily panel.</h3>
              <p>These views support the hypothesis stage without mixing incompatible raw units.</p>
            </div>
            <div className="platform-eda-grid">
              <ZoomableChart title="Spotify hours vs YouTube watched" description={chartDescriptions.spotifyYoutubeScatter}>
                <InteractiveDailyScatter
                  data={chartSeries.dailyPanel}
                  xKey="spotifyHours"
                  yKey="youtubeWatched"
                  xLabel="Spotify hours"
                  yLabel="YouTube watched"
                  color="#9ed8b3"
                />
              </ZoomableChart>
              <ZoomableChart title="Netflix + Prime count vs YouTube watched" description={chartDescriptions.longFormYoutubeScatter}>
                <InteractiveDailyScatter
                  data={chartSeries.dailyPanel}
                  xKey="netflixPrimeCount"
                  yKey="youtubeWatched"
                  xLabel="Netflix + Prime count"
                  yLabel="YouTube watched"
                  color="#d78355"
                />
              </ZoomableChart>
              <ZoomableChart title="Daily activity correlation heatmap" description={chartDescriptions.heatmap}>
                <InteractiveHeatmap data={chartSeries.correlation} />
              </ZoomableChart>
              <ZoomableChart title="Platform activity by academic period" description={chartDescriptions.youtubePeriod}>
                <InteractiveBoxPlot data={chartSeries.boxplots.youtubePeriod} title="YouTube watched by academic period" unit="records" color="#e58d55" />
              </ZoomableChart>
              <ZoomableChart title="Spotify activity by academic period" description={chartDescriptions.spotifyPeriod}>
                <InteractiveBoxPlot data={chartSeries.boxplots.spotifyPeriod} title="Spotify hours by academic period" unit="hours" color="#86b889" />
              </ZoomableChart>
              <ZoomableChart title="Long-form streaming by academic period" description={chartDescriptions.longFormPeriod}>
                <SparseActivityChart data={chartSeries.boxplots.longFormPeriod} title="Netflix + Prime active days by academic period" unit="records" color="#d78355" />
              </ZoomableChart>
              <ZoomableChart title="Platform diversity by academic period" description={chartDescriptions.platformDiversityPeriod}>
                <InteractiveBoxPlot data={chartSeries.boxplots.platformDiversityPeriod} title="Platform diversity by academic period" unit="active platforms" color="#f2c078" />
              </ZoomableChart>
              <ZoomableChart title="YouTube after-21:30 by academic period" description={chartDescriptions.youtubeAfterPeriod}>
                <InteractiveBoxPlot data={chartSeries.boxplots.youtubeAfterPeriod} title="YouTube after-21:30 by academic period" unit="records" color="#e58d55" />
              </ZoomableChart>
              <ZoomableChart title="Spotify after-21:30 by academic period" description={chartDescriptions.spotifyAfterPeriod}>
                <InteractiveBoxPlot data={chartSeries.boxplots.spotifyAfterPeriod} title="Spotify after-21:30 by academic period" unit="hours" color="#86b889" />
              </ZoomableChart>
            </div>
          </Reveal>
        </div>

        <Reveal className="combined-svg-section">
          <div className="platform-eda-copy">
            <p className="eyebrow">Combined EDA overview</p>
            <h3>Cross-platform checks.</h3>
            <p>
              They summarize coverage, active days, monthly movement, distributions, academic-period
              movement, and hourly activity before the formal hypothesis-testing section.
            </p>
          </div>
          <div className="combined-svg-grid">
            <ZoomableChart title="Dataset coverage timeline" description={chartDescriptions.coverage}>
              <CoverageTimeline data={chartSeries.coverage} commonRange={projectSummary.commonDateRange} />
            </ZoomableChart>
            <ZoomableChart title="Active days by platform" description={chartDescriptions.activeDays}>
              <ActiveDaysChart data={chartSeries.activeDays} />
            </ZoomableChart>
            <ZoomableChart title="Monthly cross-platform trends" description={chartDescriptions.monthlyTrends}>
              <MonthlyTrendChart data={chartSeries.monthlyTrends} />
            </ZoomableChart>
            <ZoomableChart title="Daily distribution overview" description={chartDescriptions.dailyDistribution}>
              <DailyDistributionSmallMultiples data={chartSeries.dailyPanel} />
            </ZoomableChart>
            <ZoomableChart title="Relative activity by academic period" description={chartDescriptions.relativeActivity}>
              <RelativeActivityChart data={chartSeries.relativeActivity} />
            </ZoomableChart>
            <ZoomableChart title="Hourly activity in Istanbul time" description={chartDescriptions.hourlyCombined}>
              <HourlyActivityChart data={chartSeries.hourlyActivity} />
            </ZoomableChart>
          </div>
        </Reveal>
      </section>

      <section className="section" id="hypotheses">
        <Reveal>
          <p className="eyebrow">Hypothesis testing</p>
          <h2 className="section-title">Hypothesis tests and current results.</h2>
          <p className="section-copy">
            The formal tests use daily variables from the same public-data panel. Final-exam comparisons use
            one-sided Mann-Whitney U tests; same-day Spotify/YouTube co-usage uses one-sided Spearman correlation.
          </p>
        </Reveal>

        <Reveal className="table-shell glass-panel">
          <p className="eyebrow">Hypothesis table</p>
          <table className="result-table desktop-table">
            <thead>
              <tr>
                <th>Hypothesis</th>
                <th>Null hypothesis (H0)</th>
                <th>Alternative hypothesis (H1)</th>
                <th>Method</th>
              </tr>
            </thead>
            <tbody>
              {hypotheses.map((hypothesis) => (
                <tr key={hypothesis.id}>
                  <td>
                    <strong>{hypothesis.id}</strong>
                    <br />
                    {hypothesis.title}
                  </td>
                  <td>{hypothesis.h0}</td>
                  <td>{hypothesis.h1}</td>
                  <td>{hypothesis.method}</td>
                </tr>
              ))}
            </tbody>
          </table>
          <div className="mobile-table-cards">
            {hypotheses.map((hypothesis) => (
              <article className="mobile-table-card" key={hypothesis.id}>
                <span className="mobile-table-kicker">{hypothesis.id}</span>
                <h3>{hypothesis.title}</h3>
                <p><strong>H0:</strong> {hypothesis.h0}</p>
                <p><strong>H1:</strong> {hypothesis.h1}</p>
                <p><strong>Method:</strong> {hypothesis.method}</p>
              </article>
            ))}
          </div>
        </Reveal>

        <Reveal className="formula-grid" delay={0.1}>
          {hypotheses.map((hypothesis) => (
            <article className="formula-card" key={hypothesis.id}>
              <span>{hypothesis.id}</span>
              <h3>{hypothesis.title}</h3>
              <p><strong>Null hypothesis (H0):</strong> {hypothesis.h0}</p>
              <p><strong>Alternative hypothesis (H1):</strong> {hypothesis.h1}</p>
              <code>{hypothesis.formula}</code>
              <small>{hypothesis.method}</small>
            </article>
          ))}
        </Reveal>

        <Reveal className="table-shell glass-panel">
          <p className="eyebrow">Complete result table</p>
          <table className="result-table desktop-table">
            <thead>
              <tr>
                <th>Hypothesis</th>
                <th>Outcome</th>
                <th>Test</th>
                <th>Statistic</th>
                <th>p-value</th>
                <th>Means</th>
                <th>Decision</th>
              </tr>
            </thead>
            <tbody>
              {projectSummary.hypothesisResults.map((result) => (
                <tr key={`${result.hypothesis}-${result.outcome}`}>
                  <td>{result.hypothesis}</td>
                  <td>{result.outcome}</td>
                  <td>{result.test}</td>
                  <td>{formatNumber(result.statistic)}</td>
                  <td>{formatPValue(result.pValue)}</td>
                  <td>{formatNumber(result.meanGroup1)} / {formatNumber(result.meanGroup2)}</td>
                  <td>{result.decision}</td>
                </tr>
              ))}
            </tbody>
          </table>
          <div className="mobile-table-cards">
            {projectSummary.hypothesisResults.map((result) => (
              <article
                className={`mobile-table-card ${result.decision === "Reject H0" ? "is-rejected" : "is-not-rejected"}`}
                key={`${result.hypothesis}-${result.outcome}`}
              >
                <div className="mobile-table-card-head">
                  <span className="mobile-table-kicker">{result.hypothesis.split(" ")[0]}</span>
                  <span className="decision-pill">{result.decision}</span>
                </div>
                <h3>{result.outcome}</h3>
                <p>{result.hypothesis}</p>
                <dl>
                  <div>
                    <dt>Test</dt>
                    <dd>{result.test}</dd>
                  </div>
                  <div>
                    <dt>p-value</dt>
                    <dd>{formatPValue(result.pValue)}</dd>
                  </div>
                  <div>
                    <dt>Statistic</dt>
                    <dd>{formatNumber(result.statistic)}</dd>
                  </div>
                  <div>
                    <dt>Means</dt>
                    <dd>{formatNumber(result.meanGroup1)} / {formatNumber(result.meanGroup2)}</dd>
                  </div>
                </dl>
              </article>
            ))}
          </div>
        </Reveal>

        <Reveal className="chart-panel">
          <p className="eyebrow">Visual result summary</p>
          <h2>Result card summary</h2>
          <HypothesisMatrix results={projectSummary.hypothesisResults} />
        </Reveal>
      </section>

      <section className="section ml-section" id="machine-learning">
        <Reveal className="ml-intro-panel">
          <div className="hero-intro-block relative z-10">
            <p className="eyebrow">Machine learning extension</p>
            <h2 className="hero-title">Predicting period labels from activity.</h2>
            <div className="project-intro">
              <p>
                <em>to be filled</em>
              </p>
              <p>
                Model results are reported with macro F1, macro precision, and macro recall so the minority
                target classes are visible instead of being hidden by overall accuracy.
              </p>
            </div>
          </div>
        </Reveal>

        <Reveal className="chart-panel">
          <p className="eyebrow">ML data preparation</p>
          <h2>Daily feature panel.</h2>
          <p>
            <em>to be filled</em>
          </p>
          <div className="ml-feature-grid" aria-label="Machine learning feature examples">
            {[
              "youtube_daily_watched_count",
              "youtube_daily_search_count",
              "spotify_daily_hours",
              "spotify_daily_stream_count",
              "netflix_prime_daily_count",
              "daily_active_platform_count",
              "youtube_after_2130_share",
              "spotify_after_2130_share",
            ].map((feature) => (
              <code key={feature}>{feature}</code>
            ))}
          </div>
        </Reveal>

        <Reveal className="chart-panel">
          <p className="eyebrow">Cumulative model comparison</p>
          <h2>Academic vs summer-work classifiers.</h2>
          <div className="ml-two-column">
            {machineLearningResults.periods.map((period) => (
              <ZoomableChart key={period.id} title={period.title} description={period.target}>
                <MLMetricComparisonChart period={period} />
              </ZoomableChart>
            ))}
          </div>
        </Reveal>

        <Reveal className="chart-panel">
          <p className="eyebrow">Best models</p>
          <h2>Best macro-F1 result by target.</h2>
          <MLBestModels periods={machineLearningResults.periods} />
        </Reveal>

        <Reveal className="chart-panel">
          <p className="eyebrow">All model confusion matrices</p>
          <h2>Model-by-model result cards.</h2>
          <MLAllModelMatrices periods={machineLearningResults.periods} />
        </Reveal>
      </section>

      <section className="section" id="appendix">
        <Reveal>
          <p className="eyebrow">Appendix</p>
          <h2 className="section-title">Notebook image gallery.</h2>
          <p className="section-copy">
            The main story above uses interactive SVG charts. The appendix keeps the original notebook PNGs
            for traceability and presentation reuse, with filters by EDA and ML group.
          </p>
          <a className="cta-link inline-block" href="#eda">
            Back to interactive EDA
          </a>
        </Reveal>
        <EdaGallery plots={appendixPlots} />
      </section>
    </main>
  );
}
