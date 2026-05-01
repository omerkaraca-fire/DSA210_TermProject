export type DatasetSummary = {
  id: string;
  name: string;
  role: string;
  rowCount: number;
  dateStart: string;
  dateEnd: string;
  publicPath: string;
  color: string;
  notes: string;
};

export type EdaPlot = {
  id: string;
  file: string;
  title: string;
  group: string;
  platform: string;
  src: string;
  caption: string;
  curated: boolean;
};

export type MachineLearningMetric = {
  model: string;
  precision: number;
  recall: number;
  f1Score: number;
};

export type MachineLearningConfusionMatrix = {
  model: string;
  source: string;
  predictedLabels: string[];
  actualLabels: string[];
  values: number[][];
};

export type MachineLearningPeriod = {
  id: string;
  title: string;
  target: string;
  labelPositive: string;
  metrics: MachineLearningMetric[];
  confusionMatrices: MachineLearningConfusionMatrix[];
};

export type MachineLearningResults = {
  periods: MachineLearningPeriod[];
};

export type HypothesisResult = {
  hypothesis: string;
  outcome: string;
  test: string;
  alternative: string;
  comparison: string;
  nGroup1: number;
  nGroup2: number;
  meanGroup1: number;
  meanGroup2: number;
  medianGroup1: number;
  medianGroup2: number;
  statistic: number;
  pValue: number;
  alpha: number;
  decision: "Reject H0" | "Do not reject H0";
  interpretation: string;
};

export type BoxPlotDatum = {
  label: string;
  min: number;
  q1: number;
  median: number;
  q3: number;
  max: number;
  mean: number;
  activeMean: number;
  activeMedian: number;
  activeCount: number;
  count: number;
};

export type ProjectSummary = {
  title: string;
  subtitle: string;
  commonDateRange: {
    start: string;
    end: string;
    days: number;
  };
  datasets: DatasetSummary[];
  edaPlots: EdaPlot[];
  hypothesisResults: HypothesisResult[];
  roadmap: string[];
};

export type ChartSeries = {
  coverage: Array<{
    platform: string;
    start: string;
    end: string;
    color: string;
  }>;
  activeDays: Array<{
    platform: string;
    activeDays: number;
    color: string;
  }>;
  monthlyTrends: Array<{
    month: string;
    youtubeWatched: number;
    spotifyHours: number;
    netflixPrimeCount: number;
  }>;
  relativeActivity: Array<{
    period: string;
    metric: string;
    value: number;
  }>;
  periodCounts: Array<{
    period: string;
    days: number;
  }>;
  correlation: {
    labels: string[];
    matrix: number[][];
  };
  dailyPanel: Array<{
    date: string;
    analysisPeriod: string;
    youtubeWatched: number;
    youtubeSearch: number;
    spotifyHours: number;
    spotifyStreams: number;
    netflixPrimeCount: number;
    platformDiversity: number;
    youtubeAfter2130Share: number;
    spotifyAfter2130Share: number;
    youtubeEstimatedWatchMinutes: number;
  }>;
  hourlyActivity: Array<{
    hour: number;
    youtubeWatched: number;
    spotifyHours: number;
  }>;
  platformEda: {
    youtube: {
      actionCounts: Array<{ label: string; value: number }>;
      targetKindCounts: Array<{ label: string; value: number }>;
      monthly: Array<{ month: string; watched: number; search: number; estimatedWatchHours: number }>;
      hourly: Array<{ hour: number; total: number; watched: number; search: number }>;
    };
    spotify: {
      monthly: Array<{ month: string; hours: number; streams: number }>;
      hourly: Array<{ hour: number; hours: number; streams: number }>;
      topArtists: Array<{ label: string; value: number }>;
      topTracks: Array<{ label: string; value: number }>;
    };
    longForm: {
      totals: Array<{ label: string; value: number }>;
      monthly: Array<{ month: string; netflix: number; prime: number; total: number }>;
      titleQuality: Array<{ label: string; value: number }>;
      recordTypes: Array<{ label: string; value: number }>;
      topNetflixTitles: Array<{ label: string; value: number }>;
      topPrimeTitles: Array<{ label: string; value: number }>;
    };
  };
  boxplots: {
    youtubeWeekday: BoxPlotDatum[];
    spotifyWeekday: BoxPlotDatum[];
    longFormWeekday: BoxPlotDatum[];
    youtubePeriod: BoxPlotDatum[];
    spotifyPeriod: BoxPlotDatum[];
    longFormPeriod: BoxPlotDatum[];
    platformDiversityPeriod: BoxPlotDatum[];
    youtubeAfterPeriod: BoxPlotDatum[];
    spotifyAfterPeriod: BoxPlotDatum[];
  };
};
