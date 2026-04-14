import chartSeriesJson from "../../public/data/chart-series.json";
import projectSummaryJson from "../../public/data/project-summary.json";
import type { ChartSeries, ProjectSummary } from "@/types";

export const projectSummary = projectSummaryJson as ProjectSummary;
export const chartSeries = chartSeriesJson as ChartSeries;

export const curatedPlots = projectSummary.edaPlots.filter((plot) => plot.curated);
export const allPlots = projectSummary.edaPlots;

export const resultGroups = [
  {
    title: "Academic pressure",
    description: "Final-exam days compared with ordinary-term days.",
    results: projectSummary.hypothesisResults.filter((result) =>
      ["H1", "H2", "H5"].some((prefix) => result.hypothesis.startsWith(prefix)),
    ),
  },
  {
    title: "Cross-platform association",
    description: "Daily relationships across platforms in the common date window.",
    results: projectSummary.hypothesisResults.filter((result) =>
      ["H3", "H4"].some((prefix) => result.hypothesis.startsWith(prefix)),
    ),
  },
];

export function formatNumber(value: number): string {
  return new Intl.NumberFormat("en", {
    maximumFractionDigits: value < 1 ? 4 : 1,
  }).format(value);
}

export function formatPValue(value: number): string {
  if (value < 0.001) {
    return "< 0.001";
  }
  return value.toFixed(4);
}
