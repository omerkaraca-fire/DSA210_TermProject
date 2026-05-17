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
    h1: "Spotify hours have a positive monotonic association with YouTube watched count.",
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

const edaGraphRows = [
  ["YouTube EDA", "YouTube activity by action", "Checks whether YouTube activity is mostly watching, searching, or other actions."],
  ["YouTube EDA", "Monthly YouTube watched and search counts", "Shows how YouTube watched and search activity changes month by month."],
  ["YouTube EDA", "Estimated continuous YouTube watch time", "Estimates rough monthly watch time using gaps between consecutive watched-video timestamps."],
  ["YouTube EDA", "YouTube activity by hour", "Shows which Istanbul-time hours have more YouTube activity."],
  ["YouTube EDA", "YouTube watched count by weekday", "Checks whether YouTube watched counts differ by weekday."],
  ["Spotify EDA", "Monthly Spotify listening", "Shows long-term Spotify listening patterns using monthly hours and stream counts."],
  ["Spotify EDA", "Spotify listening by hour", "Shows which hours have more Spotify listening activity."],
  ["Spotify EDA", "Top Spotify artists by listening hours", "Identifies the most repeated artists by total listening hours."],
  ["Spotify EDA", "Top Spotify tracks by listening minutes", "Identifies the most repeated individual songs by listening minutes."],
  ["Spotify EDA", "Spotify listening hours by weekday", "Checks whether Spotify listening differs by weekday."],
  ["Netflix + Prime Video EDA", "Long-form total count by platform", "Compares Netflix and Prime Video total row counts."],
  ["Netflix + Prime Video EDA", "Monthly long-form streaming", "Shows monthly Netflix, Prime Video, and combined long-form viewing trends."],
  ["Netflix + Prime Video EDA", "Prime Video record type split", "Checks whether Prime Video records are mostly episodes or movies."],
  ["Netflix + Prime Video EDA", "Netflix title quality", "Shows usable Netflix titles versus missing or malformed title rows."],
  ["Netflix + Prime Video EDA", "Top Netflix title groups", "Identifies the most repeated Netflix series or title groups."],
  ["Netflix + Prime Video EDA", "Top Prime Video titles", "Identifies the most repeated Prime Video series and movie titles."],
  ["Netflix + Prime Video EDA", "Long-form streaming by weekday", "Shows weekday patterns for active Netflix + Prime days, excluding zero days."],
  ["Combined EDA", "Spotify hours vs YouTube watched", "Checks same-day co-usage between Spotify hours and YouTube watched count."],
  ["Combined EDA", "Netflix + Prime count vs YouTube watched", "Checks whether long-form streaming activity relates to YouTube watched count."],
  ["Combined EDA", "Daily activity correlation heatmap", "Shows which daily platform variables move together more strongly."],
  ["Combined EDA", "Platform activity by academic period", "Compares YouTube watched count across academic periods."],
  ["Combined EDA", "Spotify activity by academic period", "Compares Spotify daily hours across academic periods."],
  ["Combined EDA", "Long-form streaming by academic period", "Compares active long-form streaming days across academic periods, excluding zero days."],
  ["Combined EDA", "Platform diversity by academic period", "Checks whether the number of active entertainment platforms changes by period."],
  ["Combined EDA", "YouTube after-21:30 by academic period", "Inspects late-evening YouTube behavior across academic periods."],
  ["Combined EDA", "Spotify after-21:30 by academic period", "Inspects late-evening Spotify listening across academic periods."],
  ["Combined EDA overview", "Dataset coverage timeline", "Shows each platform's date range and the shared comparison window."],
  ["Combined EDA overview", "Active days by platform", "Shows how many days each platform appears in the common window."],
  ["Combined EDA overview", "Monthly cross-platform trends", "Compares monthly YouTube watched count, Spotify hours, and Netflix + Prime count in separate panels."],
  ["Combined EDA overview", "Daily distribution overview", "Shows skew, zero-heavy behavior, and outliers in daily variables."],
  ["Combined EDA overview", "Relative activity by academic period", "Compares period averages after scaling by overall averages."],
  ["Combined EDA overview", "Hourly activity in Istanbul time", "Compares YouTube and Spotify time-of-day behavior in Istanbul time."],
];

const edaInterpretations = [
  "The datasets have different initial dates. Therefore, the Dataset Coverage Timeline shows the starting date of each dataset. The common coverage period starts on 17 April 2022.",
  "Active Days by Platform examines how many days each platform appears in the dataset, using a count-based approach.",
  "Hourly Activity in Istanbul Time examines discrete hourly events in a cumulative format. However, this analysis is only performed for entries with appropriate timestamps, where the exact time is available. Therefore, YouTube and Spotify were the suitable platforms for this analysis.",
  "Relative Activity by Academic Period examines all events according to predefined academic-period classes. These classes are finals, ordinary days, summer work, and outside. The outside category is excluded from the machine learning analysis because the number and type of daily events during those days cannot be determined reliably. For example, the subject may have been working, studying, or doing another activity.",
  "The remaining graphs can be examined for further understanding.",
];

const hypothesisInterpretations = [
  <>First, the p-values of the first three hypotheses are higher than 0.05, so <strong>there is no evidence to reject the null hypothesis.</strong></>,
  <>For the last two hypotheses, H4 and H5, related to YouTube and Spotify, the p-values are smaller than 0.05. This means that the null hypothesis is <strong>rejected in favor of the alternative hypothesis</strong>, because the probability of observing such results under the null hypothesis is very low.</>,
  <>Not rejecting the null hypothesis for H1 might imply that the subject user <strong>does not significantly change their usage behavior during exam periods</strong> and uses the platform similarly to ordinary periods.</>,
  "Not rejecting the null hypothesis for H2 suggests a similar interpretation to H1.",
  <>Not rejecting the null hypothesis for H3 might suggest that the subject <strong>does not use YouTube significantly less when also using Netflix and Prime Video.</strong></>,
  <>For H4, the result shows a <strong>statistically significant positive</strong> association between Spotify hours and YouTube watched count. However, the <strong>relationship is weak</strong>. The Spearman correlation coefficient is <strong>ρ = 0.0934, which is close to zero</strong>. This means that Spotify and YouTube usage tend to <strong>increase together slightly</strong>, but the relationship <strong>should not be interpreted as strong.</strong></>,
  <>For H5, the <strong>late-evening entertainment</strong> result suggests that Spotify and YouTube usage during final periods <strong>was lower compared to ordinary days.</strong></>,
];

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

        <Reveal className="eda-context-panel glass-panel" delay={0.05}>
          <p>
            <em>The exploratory data analysis (EDA) below examines the following data points:</em>
          </p>
          <details className="expandable-table">
            <summary>
              <span>Table of graphs</span>
              <small>{edaGraphRows.length} graphs</small>
            </summary>
            <div className="table-shell">
              <table className="result-table eda-graph-table">
                <thead>
                  <tr>
                    <th>EDA section</th>
                    <th>Graph</th>
                    <th>What it inspects</th>
                  </tr>
                </thead>
                <tbody>
                  {edaGraphRows.map(([section, graph, inspection]) => (
                    <tr key={`${section}-${graph}`}>
                      <td>{section}</td>
                      <td>{graph}</td>
                      <td>{inspection}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </details>
          <div className="eda-interpretation-copy">
            <p>
              <em>Based on the graphs, there is a significant amount of information that requires further interpretation.</em>
            </p>
            <p>
              <em>
                For this reason, I tried to examine these graphs as thoroughly as possible. The corresponding
                Matplotlib versions are also included in the appendix.
              </em>
            </p>
            <p>
              <em>Some important findings and interpretations are as follows:</em>
            </p>
            <ul className="interpretation-list">
              {edaInterpretations.map((interpretation) => (
                <li key={interpretation}>
                  <em>{interpretation}</em>
                </li>
              ))}
            </ul>
          </div>
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

        <Reveal className="hypothesis-context-panel glass-panel" delay={0.05}>
          <div className="hypothesis-context-copy">
            <h3>Hypothesis testing</h3>
            <p><em>There are five hypotheses to be inspected in the table below.</em></p>
            <p>
              <em>
                The Mann-Whitney U test is used for the group comparisons because the daily activity
                variables are skewed and zero-heavy. Therefore, <strong>a rank-based non-parametric test is
                more suitable</strong> than assuming normally distributed data.
              </em>
            </p>
            <p>
              <em>
                Spearman correlation is used for the Spotify and YouTube relationship because it checks
                whether two variables move together monotonically without requiring a linear relationship.
              </em>
            </p>
            <p><em>Results and interpretations below:</em></p>
          </div>
          <ul className="interpretation-list">
            {hypothesisInterpretations.map((interpretation, index) => (
              <li key={index}>
                <em>{interpretation}</em>
              </li>
            ))}
          </ul>
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
            <div className="project-intro ml-narrative">
              <p>
                <em>This part examines the ML work of the project.</em>
              </p>
              <p>
                <em>
                  First, I examined my dataset to find a goal where ML models could be used. Given the number
                  of daily activities, I asked whether it would be possible to guess my day&apos;s class, where the
                  class corresponds to normal day, final exam period, or summer work period.
                </em>
              </p>
              <p>
                <em>
                  To illustrate better, exam period corresponds to the final exam period. <strong>Midterm dates
                  are not separately labeled here; if they fall outside the final exam period, they remain inside
                  the ordinary term class</strong>, due to each course distributing its workload in different time
                  periods. The summer work period is the time where I worked in summers as an intern in a local
                  company in my hometown, and the ordinary time period is the remaining days. Except for some
                  outliers, most certainly, the years can be differentiated into these three groups.
                </em>
              </p>
              <p>
                <em>
                  Thus, as in the EDA and hypothesis testing, I used the academic calendar of Sabanci University
                  to determine those dates. In that manner, I classified the dates as ordinary term date, summer
                  work period, and final exam based on analysis_period.
                </em>
              </p>
              <div className="ml-table-grid">
                <div className="table-shell">
                  <p className="eyebrow">analysis_period</p>
                  <table className="result-table ml-narrative-table">
                    <thead>
                      <tr>
                        <th>Value</th>
                        <th>Meaning</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr>
                        <td><code>ordinary_term</code></td>
                        <td>Regular academic term days</td>
                      </tr>
                      <tr>
                        <td><code>final_exam</code></td>
                        <td>Final exam period days</td>
                      </tr>
                      <tr>
                        <td><code>summer_work_period</code></td>
                        <td>Summer term/work period days</td>
                      </tr>
                      <tr>
                        <td><code>outside_calendar</code></td>
                        <td>Days outside the labeled academic calendar</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
                <div className="table-shell">
                  <p className="eyebrow">Classification tasks</p>
                  <table className="result-table ml-narrative-table">
                    <thead>
                      <tr>
                        <th>Task</th>
                        <th>Classes Included</th>
                        <th>Full</th>
                        <th>Train</th>
                        <th>Test</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr>
                        <td>Final Exam vs Ordinary Term</td>
                        <td><code>ordinary_term</code>, <code>final_exam</code></td>
                        <td>872</td>
                        <td>697</td>
                        <td>175</td>
                      </tr>
                      <tr>
                        <td>Summer Work vs Ordinary Term</td>
                        <td><code>ordinary_term</code>, <code>summer_work_period</code></td>
                        <td>979</td>
                        <td>783</td>
                        <td>196</td>
                      </tr>
                      <tr>
                        <td>All Periods Classification</td>
                        <td><code>ordinary_term</code>, <code>final_exam</code>, <code>summer_work_period</code></td>
                        <td>1076</td>
                        <td>860</td>
                        <td>216</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
              <div className="ml-feature-columns">
                <div>
                  <p className="eyebrow">Final Exam ML and All Class</p>
                  <div className="ml-feature-grid" aria-label="Common machine learning feature columns">
                    {[
                      "youtube_daily_watched_count",
                      "youtube_daily_search_count",
                      "youtube_after_2130_count",
                      "spotify_daily_hours",
                      "spotify_daily_stream_count",
                      "spotify_daily_unique_tracks",
                      "spotify_after_2130_hours",
                      "netflix_daily_count",
                      "prime_video_daily_count",
                      "netflix_prime_daily_count",
                      "daily_distinct_entertainment_platform_count",
                    ].map((feature) => (
                      <code key={feature}>{feature}</code>
                    ))}
                  </div>
                </div>
                <div>
                  <p className="eyebrow">Additional Features For Summer Working Period</p>
                  <div className="ml-feature-grid" aria-label="Summer work machine learning feature columns">
                    {["youtube_after_2130_share", "spotify_after_2130_hour_share"].map((feature) => (
                      <code key={feature}>{feature}</code>
                    ))}
                  </div>
                </div>
              </div>
              <p>
                <em>
                  The ML classification is intentionally separated due to sequential development and how I
                  decided to develop it. Classification happened in three ways: ordinary term or final exam
                  period, summer time work period or ordinary term, and the combined three-class classification.
                </em>
              </p>
              <div className="table-shell">
                <p className="eyebrow">Cross-validation and parameter tuning</p>
                <table className="result-table ml-narrative-table">
                  <thead>
                    <tr>
                      <th>Classification Task</th>
                      <th>Train/Test Split</th>
                      <th>Cross-Validation</th>
                      <th>Tuning Criterion</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      <td>Final Exam vs Ordinary Term</td>
                      <td>80/20 stratified split</td>
                      <td>5-fold StratifiedKFold on training data</td>
                      <td>Macro F1</td>
                    </tr>
                    <tr>
                      <td>Summer Work vs Ordinary Term</td>
                      <td>80/20 stratified split</td>
                      <td>5-fold StratifiedKFold on training data</td>
                      <td>Macro F1</td>
                    </tr>
                    <tr>
                      <td>All Periods Classification</td>
                      <td>80/20 stratified split</td>
                      <td>5-fold StratifiedKFold on training data</td>
                      <td>Macro F1</td>
                    </tr>
                  </tbody>
                </table>
              </div>
              <p>
                <em>
                  Based on those features, I used Dummy Classifier, Logistic Regression, Decision Tree, XGBoost,
                  Random Forest, and an Ensemble Model that votes across the previous models. DBSCAN is
                  included as an unsupervised comparison, where clusters are mapped to labels after fitting.
                </em>
              </p>
              <p>
                <em>
                  The supervised models are tuned with GridSearchCV on the training set, while the held-out test
                  set is used only for final evaluation. Logistic Regression tunes regularization choices, Decision
                  Tree tunes tree-shape and class-weight settings, XGBoost tunes boosting/tree settings where
                  GridSearchCV is used, Random Forest tunes forest and tree-size settings, and the ensemble tunes
                  voting type and model weights. DBSCAN tunes eps and min_samples using silhouette score.
                </em>
              </p>
              <div className="table-shell">
                <p className="eyebrow">Voting ensemble components</p>
                <table className="result-table ml-narrative-table">
                  <thead>
                    <tr>
                      <th>Classification Task</th>
                      <th>Models Used Inside Ensemble</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      <td>Final Exam vs Ordinary Term</td>
                      <td>Logistic Regression, tuned Decision Tree, XGBoost, Random Forest</td>
                    </tr>
                    <tr>
                      <td>Summer Work vs Ordinary Term</td>
                      <td>Summer Logistic Regression, tuned Summer Decision Tree, Summer XGBoost, Summer Random Forest</td>
                    </tr>
                    <tr>
                      <td>All Periods Classification</td>
                      <td>All-class Logistic Regression, tuned All-class Decision Tree, All-class XGBoost, All-class Random Forest</td>
                    </tr>
                  </tbody>
                </table>
              </div>
              <p>
                <em>
                  For final exam period versus ordinary term, the dummy classifier macro-F1 was 47.1%, and the
                  best macro-F1 was XGBoost and the ensemble model with 51.8%. This is an improvement of <strong>4.72
                  percentage points</strong>, or <strong>10.01%</strong> relative improvement, suggesting that
                  parameter tuning improved the baseline but the current features still provide limited predictive
                  signal for distinguishing final exam days from ordinary term days.
                </em>
              </p>
              <p>
                <em>
                  For summer work period versus ordinary term, the dummy classifier macro-F1 was 44.2%, while
                  the best macro-F1 was <strong>68.6%</strong> with the ensemble model. This is an improvement
                  of <strong>24.43 percentage points</strong>, or <strong>55.32%</strong> relative improvement,
                  suggesting that parameter tuning and the available features capture summer work behavior more
                  clearly than final exam behavior.
                </em>
              </p>
              <p>
                <em>
                  For the combined three-class classification, the dummy classifier macro-F1 was 28.0%, while
                  the best macro-F1 was <strong>44.5%</strong> with XGBoost. This is an improvement
                  of <strong>16.56 percentage points</strong>, or <strong>59.25%</strong> relative improvement
                  after parameter tuning.
                </em>
              </p>
              <div className="table-shell">
                <table className="result-table ml-narrative-table">
                  <thead>
                    <tr>
                      <th>Classification Task</th>
                      <th>Dummy Macro F1</th>
                      <th>Best Model</th>
                      <th>Best Model Macro F1</th>
                      <th>Absolute Increase</th>
                      <th>Relative Improvement</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      <td>Final Exam vs Ordinary Term</td>
                      <td>47.13%</td>
                      <td>XGBoost / Ensemble Model</td>
                      <td>51.85%</td>
                      <td>+4.72 percentage points</td>
                      <td>+10.01%</td>
                    </tr>
                    <tr>
                      <td>Summer Work vs Ordinary Term</td>
                      <td>44.16%</td>
                      <td>Ensemble Model</td>
                      <td>68.59%</td>
                      <td>+24.43 percentage points</td>
                      <td>+55.32%</td>
                    </tr>
                    <tr>
                      <td>All Periods: Ordinary vs Final vs Summer</td>
                      <td>27.96%</td>
                      <td>XGBoost</td>
                      <td>44.52%</td>
                      <td>+16.56 percentage points</td>
                      <td>+59.25%</td>
                    </tr>
                  </tbody>
                </table>
              </div>
              <p>
                <em>
                  In conclusion, the separation hinted that the summer work period pattern is easier to capture
                  with the available features. The current features were not enough to strongly differentiate the
                  final period and ordinary period. This can happen either because the final exam period is not
                  very different from ordinary term behavior, or because important social-media signals are still
                  excluded from the current feature set.
                </em>
              </p>
              <div className="ml-next-objectives">
                <p>
                  <em><strong>Current model note:</strong></em>
                </p>
                <ul>
                  <li><em>The second ML notebook adds cross-validation and parameter tuning for the main supervised models.</em></li>
                  <li><em>DBSCAN replaces the earlier clustering comparison because it can capture irregular clusters and noise points.</em></li>
                </ul>
              </div>
            </div>
          </div>
        </Reveal>

        <Reveal className="chart-panel">
          <p className="eyebrow">Cumulative model comparison</p>
          <h2>Three classification tasks.</h2>
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
            for traceability and presentation reuse, with one selected image per EDA and ML group.
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
