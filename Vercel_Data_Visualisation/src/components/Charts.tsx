"use client";

import * as d3 from "d3";
import { motion } from "framer-motion";
import { useState } from "react";
import type { ChartSeries, HypothesisResult } from "@/types";
import { formatPValue } from "@/lib/data";

type DailyPanelRow = ChartSeries["dailyPanel"][number];
type DailyMetricKey = Exclude<keyof DailyPanelRow, "date" | "analysisPeriod">;

type CoverageTimelineProps = {
  data: ChartSeries["coverage"];
  commonRange: { start: string; end: string; days: number };
};

function ChartTooltip({ x, y, lines }: { x: number; y: number; lines: string[] }) {
  const width = Math.max(190, Math.max(...lines.map((line) => line.length)) * 7.8);
  const height = 30 + lines.length * 20;
  const xPos = Math.min(Math.max(8, x + 14), 900 - width - 8);
  const yPos = Math.max(8, y - height - 12);

  return (
    <g className="svg-tooltip" pointerEvents="none">
      <rect x={xPos} y={yPos} width={width} height={height} rx={14} />
      {lines.map((line, index) => (
        <text key={`${line}-${index}`} x={xPos + 14} y={yPos + 24 + index * 20}>
          {line}
        </text>
      ))}
    </g>
  );
}

export function CoverageTimeline({ data, commonRange }: CoverageTimelineProps) {
  const [hovered, setHovered] = useState<ChartSeries["coverage"][number] | null>(null);
  const width = 880;
  const height = 280;
  const margin = { top: 36, right: 28, bottom: 42, left: 130 };
  const minDate = d3.min(data, (d) => new Date(d.start)) ?? new Date(commonRange.start);
  const maxDate = d3.max(data, (d) => new Date(d.end)) ?? new Date(commonRange.end);
  const x = d3.scaleTime().domain([minDate, maxDate]).range([margin.left, width - margin.right]);
  const y = d3
    .scaleBand()
    .domain(data.map((d) => d.platform))
    .range([margin.top, height - margin.bottom])
    .padding(0.35);
  const ticks = x.ticks(5);
  const commonStart = x(new Date(commonRange.start));
  const commonEnd = x(new Date(commonRange.end));

  return (
    <svg className="chart-svg interactive-svg" viewBox={`0 0 ${width} ${height}`} role="img">
      <title>Public dataset date coverage</title>
      <g>
        {ticks.map((tick) => (
          <g key={tick.toISOString()}>
            <line x1={x(tick)} x2={x(tick)} y1={margin.top - 8} y2={height - margin.bottom + 12} stroke="rgba(255,255,255,0.08)" />
            <text x={x(tick)} y={height - 12} textAnchor="middle" className="chart-axis">
              {tick.getFullYear()}
            </text>
          </g>
        ))}
      </g>
      <rect x={commonStart} y={margin.top - 18} width={commonEnd - commonStart} height={height - margin.top - margin.bottom + 28} fill="rgba(125,215,186,0.08)" rx={18} />
      {data.map((item, index) => {
        const yPos = y(item.platform) ?? 0;
        return (
          <motion.g
            key={item.platform}
            initial={{ opacity: 0, x: -16 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            transition={{ delay: index * 0.08 }}
          >
            <text x={margin.left - 18} y={yPos + y.bandwidth() / 2 + 5} textAnchor="end" className="chart-label">
              {item.platform}
            </text>
            <rect
              x={x(new Date(item.start))}
              y={yPos}
              width={x(new Date(item.end)) - x(new Date(item.start))}
              height={y.bandwidth()}
              rx={10}
              fill={item.color}
              opacity={hovered === null || hovered.platform === item.platform ? 0.9 : 0.28}
              stroke={hovered?.platform === item.platform ? "#fff1cf" : "transparent"}
              strokeWidth={hovered?.platform === item.platform ? 3 : 0}
              onMouseEnter={() => setHovered(item)}
              onMouseLeave={() => setHovered(null)}
            />
          </motion.g>
        );
      })}
      <line x1={commonStart} x2={commonStart} y1={24} y2={height - 36} stroke="#f0eadb" strokeDasharray="5 5" />
      <line x1={commonEnd} x2={commonEnd} y1={24} y2={height - 36} stroke="#f0eadb" strokeDasharray="5 5" />
      <text x={(commonStart + commonEnd) / 2} y={24} textAnchor="middle" className="chart-note">
        common testing range: {commonRange.start} to {commonRange.end}
      </text>
      {hovered ? (
        <ChartTooltip
          x={x(new Date(hovered.end))}
          y={y(hovered.platform) ?? margin.top}
          lines={[hovered.platform, `${hovered.start} to ${hovered.end}`, `Common window: ${commonRange.days} days`]}
        />
      ) : null}
    </svg>
  );
}

export function ActiveDaysChart({ data }: { data: ChartSeries["activeDays"] }) {
  const [hovered, setHovered] = useState<ChartSeries["activeDays"][number] | null>(null);
  const width = 760;
  const height = 330;
  const margin = { top: 28, right: 24, bottom: 48, left: 72 };
  const maxValue = d3.max(data, (d) => d.activeDays) ?? 1;
  const x = d3
    .scaleBand()
    .domain(data.map((d) => d.platform))
    .range([margin.left, width - margin.right])
    .padding(0.25);
  const y = d3.scaleLinear().domain([0, maxValue]).nice().range([height - margin.bottom, margin.top]);

  return (
    <svg className="chart-svg interactive-svg" viewBox={`0 0 ${width} ${height}`} role="img">
      <title>Active days by platform</title>
      {y.ticks(4).map((tick) => (
        <g key={tick}>
          <line x1={margin.left} x2={width - margin.right} y1={y(tick)} y2={y(tick)} stroke="rgba(255,255,255,0.08)" />
          <text x={margin.left - 12} y={y(tick) + 4} textAnchor="end" className="chart-axis">
            {tick}
          </text>
        </g>
      ))}
      {data.map((item, index) => {
        const xPos = x(item.platform) ?? 0;
        const barHeight = height - margin.bottom - y(item.activeDays);
        return (
          <motion.g
            key={item.platform}
            initial={{ opacity: 0, y: 16 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: index * 0.08 }}
          >
            <rect
              x={xPos}
              y={y(item.activeDays)}
              width={x.bandwidth()}
              height={barHeight}
              rx={14}
              fill={item.color}
              opacity={hovered === null || hovered.platform === item.platform ? 0.92 : 0.28}
              stroke={hovered?.platform === item.platform ? "#fff1cf" : "transparent"}
              strokeWidth={hovered?.platform === item.platform ? 3 : 0}
              onMouseEnter={() => setHovered(item)}
              onMouseLeave={() => setHovered(null)}
            />
            <text x={xPos + x.bandwidth() / 2} y={y(item.activeDays) - 10} textAnchor="middle" className="chart-value">
              {item.activeDays}
            </text>
            <text x={xPos + x.bandwidth() / 2} y={height - 16} textAnchor="middle" className="chart-axis">
              {item.platform}
            </text>
          </motion.g>
        );
      })}
      {hovered ? (
        <ChartTooltip
          x={(x(hovered.platform) ?? margin.left) + x.bandwidth()}
          y={y(hovered.activeDays)}
          lines={[hovered.platform, `${hovered.activeDays} active days`]}
        />
      ) : null}
    </svg>
  );
}

export function MonthlyTrendChart({ data }: { data: ChartSeries["monthlyTrends"] }) {
  const [hovered, setHovered] = useState<{
    item: ChartSeries["monthlyTrends"][number];
    panel: { key: "youtubeWatched" | "spotifyHours" | "netflixPrimeCount"; label: string; unit: string; color: string };
  } | null>(null);
  const width = 900;
  const height = 520;
  const margin = { top: 36, right: 34, bottom: 46, left: 78 };
  const dates = data.map((d) => new Date(d.month));
  const x = d3
    .scaleTime()
    .domain(d3.extent(dates) as [Date, Date])
    .range([margin.left, width - margin.right]);
  const panels = [
    {
      key: "youtubeWatched" as const,
      label: "YouTube watched",
      unit: "monthly records",
      color: "#5db5f0",
    },
    {
      key: "spotifyHours" as const,
      label: "Spotify listening",
      unit: "monthly hours",
      color: "#7dd7ba",
    },
    {
      key: "netflixPrimeCount" as const,
      label: "Netflix + Prime",
      unit: "monthly views",
      color: "#d29355",
    },
  ];
  const panelGap = 24;
  const panelHeight = (height - margin.top - margin.bottom - panelGap * (panels.length - 1)) / panels.length;

  return (
    <svg className="chart-svg interactive-svg" viewBox={`0 0 ${width} ${height}`} role="img">
      <title>Monthly cross-platform trends as small multiples</title>
      {panels.map((panel, index) => {
        const panelTop = margin.top + index * (panelHeight + panelGap);
        const panelBottom = panelTop + panelHeight;
        const maxValue = Math.max(1, d3.max(data, (d) => Number(d[panel.key])) ?? 1);
        const y = d3.scaleLinear().domain([0, maxValue]).nice().range([panelBottom, panelTop]);
        const path = d3
          .line<(typeof data)[number]>()
          .x((d) => x(new Date(d.month)))
          .y((d) => y(Number(d[panel.key])))
          .curve(d3.curveCatmullRom.alpha(0.5))(data);
        return (
          <g key={panel.key}>
            <line x1={margin.left} x2={width - margin.right} y1={panelBottom} y2={panelBottom} stroke="rgba(255,255,255,0.12)" />
            {y.ticks(3).map((tick) => (
              <g key={`${panel.key}-${tick}`}>
                <line x1={margin.left} x2={width - margin.right} y1={y(tick)} y2={y(tick)} stroke="rgba(255,255,255,0.07)" />
                <text x={margin.left - 12} y={y(tick) + 5} textAnchor="end" className="chart-axis">
                  {tick}
                </text>
              </g>
            ))}
            <text x={margin.left} y={panelTop - 10} className="chart-label">
              {panel.label}
            </text>
            <text x={width - margin.right} y={panelTop - 10} textAnchor="end" className="chart-note">
              {panel.unit}
            </text>
            <motion.path
              d={path ?? ""}
              fill="none"
              stroke={panel.color}
              strokeWidth={3.5}
              initial={{ pathLength: 0, opacity: 0 }}
              whileInView={{ pathLength: 1, opacity: 1 }}
              viewport={{ once: true }}
              transition={{ duration: 1, delay: index * 0.16 }}
            >
              <title>{`${panel.label}, ${panel.unit}`}</title>
            </motion.path>
            {data.map((item) => {
              const isHovered = hovered?.item.month === item.month && hovered.panel.key === panel.key;
              return (
                <circle
                  key={`${panel.key}-${item.month}`}
                  cx={x(new Date(item.month))}
                  cy={y(Number(item[panel.key]))}
                  r={isHovered ? 7 : 4}
                  fill={panel.color}
                  opacity={hovered === null || isHovered ? 0.92 : 0.2}
                  stroke={isHovered ? "#fff1cf" : "transparent"}
                  strokeWidth={isHovered ? 3 : 0}
                  onMouseEnter={() => setHovered({ item, panel })}
                  onMouseLeave={() => setHovered(null)}
                />
              );
            })}
          </g>
        );
      })}
      {x.ticks(6).map((tick) => (
        <text key={tick.toISOString()} x={x(tick)} y={height - 14} textAnchor="middle" className="chart-axis">
          {tick.getFullYear()}
        </text>
      ))}
      <text x={width - margin.right} y={height - 14} textAnchor="end" className="chart-note">
        Each panel has its own y-axis.
      </text>
      {hovered ? (
        <ChartTooltip
          x={x(new Date(hovered.item.month))}
          y={margin.top + panels.findIndex((panel) => panel.key === hovered.panel.key) * (panelHeight + panelGap) + panelHeight / 2}
          lines={[hovered.item.month.slice(0, 7), hovered.panel.label, `${Number(hovered.item[hovered.panel.key]).toFixed(2)} ${hovered.panel.unit}`]}
        />
      ) : null}
    </svg>
  );
}

export function RelativeActivityChart({ data }: { data: ChartSeries["relativeActivity"] }) {
  const [hovered, setHovered] = useState<ChartSeries["relativeActivity"][number] | null>(null);
  const width = 820;
  const height = 420;
  const margin = { top: 32, right: 24, bottom: 78, left: 60 };
  const periods = Array.from(new Set(data.map((d) => d.period)));
  const metrics = Array.from(new Set(data.map((d) => d.metric)));
  const x0 = d3.scaleBand().domain(periods).range([margin.left, width - margin.right]).padding(0.18);
  const x1 = d3.scaleBand().domain(metrics).range([0, x0.bandwidth()]).padding(0.12);
  const y = d3.scaleLinear().domain([0, 1.55]).range([height - margin.bottom, margin.top]);
  const colors = d3.scaleOrdinal<string>().domain(metrics).range(["#5db5f0", "#7dd7ba", "#d29355", "#cda5ff"]);
  const periodLabel = (period: string) =>
    ({
      ordinary_term: "Ordinary",
      final_exam: "Finals",
      outside_calendar: "Outside",
      summer_work_period: "Summer work",
    })[period] ?? period.replaceAll("_", " ");

  return (
    <svg className="chart-svg interactive-svg" viewBox={`0 0 ${width} ${height}`} role="img">
      <title>Relative activity by analysis period</title>
      <line x1={margin.left} x2={width - margin.right} y1={y(1)} y2={y(1)} stroke="#f0eadb" strokeDasharray="6 6" />
      <text x={width - margin.right} y={y(1) - 8} textAnchor="end" className="chart-note">
        overall average
      </text>
      {periods.map((period) => (
        <g key={period} transform={`translate(${x0(period)}, 0)`}>
          {metrics.map((metric) => {
            const row = data.find((item) => item.period === period && item.metric === metric);
            const value = row?.value ?? 0;
            return (
              <rect
                key={metric}
                x={x1(metric)}
                y={y(value)}
                width={x1.bandwidth()}
                height={height - margin.bottom - y(value)}
                rx={7}
                fill={colors(metric)}
                opacity={hovered === null || (hovered.period === period && hovered.metric === metric) ? 0.92 : 0.24}
                stroke={hovered?.period === period && hovered.metric === metric ? "#fff1cf" : "transparent"}
                strokeWidth={hovered?.period === period && hovered.metric === metric ? 3 : 0}
                onMouseEnter={() => row && setHovered(row)}
                onMouseLeave={() => setHovered(null)}
              >
                <title>{`${period.replaceAll("_", " ")} ${metric}: ${value.toFixed(2)} relative to average`}</title>
              </rect>
            );
          })}
          <text x={x0.bandwidth() / 2} y={height - 38} textAnchor="middle" className="chart-axis">
            {periodLabel(period)}
          </text>
        </g>
      ))}
      <g transform={`translate(${margin.left}, ${height - 16})`}>
        {metrics.map((metric, index) => (
          <g key={metric} transform={`translate(${index * 180}, 0)`}>
            <circle r={5} fill={colors(metric)} />
            <text x={10} y={4} className="chart-note">
              {metric}
            </text>
          </g>
        ))}
      </g>
      {hovered ? (
        <ChartTooltip
          x={(x0(hovered.period) ?? margin.left) + x0.bandwidth()}
          y={y(hovered.value)}
          lines={[periodLabel(hovered.period), hovered.metric, `${hovered.value.toFixed(2)}x overall average`]}
        />
      ) : null}
    </svg>
  );
}

export function PipelineDiagram() {
  const steps = [
    { title: "Public exports", note: "YouTube, Spotify, Netflix, Prime Video" },
    { title: "Processing scripts", note: "Normalize fields and protect identifiers" },
    { title: "fine_* schema", note: "Shared dates, timestamps, and platform labels" },
    { title: "Daily panel", note: "One row per date across platforms" },
    { title: "EDA and tests", note: "Plots, hypotheses, and current basic results" },
  ];
  return (
    <svg className="chart-svg interactive-svg" viewBox="0 0 980 260" role="img">
      <title>Project processing pipeline</title>
      {steps.map((step, index) => {
        const x = 38 + index * 185;
        return (
          <g key={step.title}>
            <rect x={x} y={72} width={150} height={104} rx={22} fill="rgba(255,255,255,0.08)" stroke="rgba(255,255,255,0.18)" />
            <text x={x + 75} y={112} textAnchor="middle" className="chart-label">
              {step.title}
            </text>
            <foreignObject x={x + 16} y={122} width={118} height={44}>
              <p className="diagram-note">{step.note}</p>
            </foreignObject>
            {index < steps.length - 1 ? (
              <path d={`M ${x + 150} 124 L ${x + 180} 124`} stroke="#7dd7ba" strokeWidth={3} markerEnd="url(#arrow)" />
            ) : null}
          </g>
        );
      })}
      <defs>
        <marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
          <path d="M 0 0 L 10 5 L 0 10 z" fill="#7dd7ba" />
        </marker>
      </defs>
    </svg>
  );
}

export function CorrelationHeatmap({ data }: { data: ChartSeries["correlation"] }) {
  const [hovered, setHovered] = useState<{ row: number; column: number; value: number } | null>(null);
  const width = 860;
  const height = 760;
  const margin = { top: 150, right: 30, bottom: 36, left: 210 };
  const labels = data.labels;
  const cellSize = Math.min((width - margin.left - margin.right) / labels.length, (height - margin.top - margin.bottom) / labels.length);
  const color = d3.scaleSequential((value: number) => d3.interpolateRdBu(1 - value)).domain([-1, 1]);

  return (
    <svg className="chart-svg interactive-svg" viewBox={`0 0 ${width} ${height}`} role="img">
      <title>Spearman daily-variable correlation heatmap</title>
      {labels.map((label, index) => (
        <g key={`label-${label}`}>
          <text
            x={margin.left + index * cellSize + cellSize / 2}
            y={margin.top - 14}
            textAnchor="end"
            className="chart-axis"
            transform={`rotate(-45 ${margin.left + index * cellSize + cellSize / 2} ${margin.top - 14})`}
          >
            {label}
          </text>
          <text x={margin.left - 12} y={margin.top + index * cellSize + cellSize / 2 + 5} textAnchor="end" className="chart-axis">
            {label}
          </text>
        </g>
      ))}
      {data.matrix.map((row, rowIndex) =>
        row.map((value, columnIndex) => (
          <g key={`${rowIndex}-${columnIndex}`}>
            <rect
              x={margin.left + columnIndex * cellSize}
              y={margin.top + rowIndex * cellSize}
              width={cellSize - 2}
              height={cellSize - 2}
              rx={8}
              fill={color(value)}
              opacity={hovered === null || (hovered.row === rowIndex && hovered.column === columnIndex) ? 0.9 : 0.24}
              stroke={hovered?.row === rowIndex && hovered.column === columnIndex ? "#fff1cf" : "transparent"}
              strokeWidth={hovered?.row === rowIndex && hovered.column === columnIndex ? 3 : 0}
              onMouseEnter={() => setHovered({ row: rowIndex, column: columnIndex, value })}
              onMouseLeave={() => setHovered(null)}
            />
            <text
              x={margin.left + columnIndex * cellSize + cellSize / 2}
              y={margin.top + rowIndex * cellSize + cellSize / 2 + 5}
              textAnchor="middle"
              className="heatmap-value"
            >
              {value.toFixed(2)}
            </text>
          </g>
        )),
      )}
      {hovered ? (
        <ChartTooltip
          x={margin.left + hovered.column * cellSize + cellSize}
          y={margin.top + hovered.row * cellSize}
          lines={[labels[hovered.row], labels[hovered.column], `rho = ${hovered.value.toFixed(2)}`]}
        />
      ) : null}
    </svg>
  );
}

export function DailyScatterChart({
  data,
  xKey,
  yKey,
  xLabel,
  yLabel,
  color = "#7dd7ba",
}: {
  data: ChartSeries["dailyPanel"];
  xKey: DailyMetricKey;
  yKey: DailyMetricKey;
  xLabel: string;
  yLabel: string;
  color?: string;
}) {
  const [hovered, setHovered] = useState<ChartSeries["dailyPanel"][number] | null>(null);
  const width = 820;
  const height = 520;
  const margin = { top: 34, right: 34, bottom: 72, left: 88 };
  const xMax = Math.max(1, d3.max(data, (d) => Number(d[xKey])) ?? 1);
  const yMax = Math.max(1, d3.max(data, (d) => Number(d[yKey])) ?? 1);
  const x = d3.scaleLinear().domain([0, xMax]).nice().range([margin.left, width - margin.right]);
  const y = d3.scaleLinear().domain([0, yMax]).nice().range([height - margin.bottom, margin.top]);

  return (
    <svg className="chart-svg interactive-svg" viewBox={`0 0 ${width} ${height}`} role="img">
      <title>{`${yLabel} by ${xLabel}`}</title>
      {x.ticks(5).map((tick) => (
        <g key={`x-${tick}`}>
          <line x1={x(tick)} x2={x(tick)} y1={margin.top} y2={height - margin.bottom} stroke="rgba(255,255,255,0.06)" />
          <text x={x(tick)} y={height - 34} textAnchor="middle" className="chart-axis">
            {tick}
          </text>
        </g>
      ))}
      {y.ticks(5).map((tick) => (
        <g key={`y-${tick}`}>
          <line x1={margin.left} x2={width - margin.right} y1={y(tick)} y2={y(tick)} stroke="rgba(255,255,255,0.08)" />
          <text x={margin.left - 12} y={y(tick) + 5} textAnchor="end" className="chart-axis">
            {tick}
          </text>
        </g>
      ))}
      {data.map((item) => (
        <circle
          key={`${item.date}-${item[xKey]}-${item[yKey]}`}
          cx={x(Number(item[xKey]))}
          cy={y(Number(item[yKey]))}
          r={4.2}
          fill={color}
          opacity={hovered === null || hovered.date === item.date ? (item.analysisPeriod === "final_exam" ? 0.86 : 0.36) : 0.08}
          stroke={hovered?.date === item.date || item.analysisPeriod === "final_exam" ? "#f0eadb" : "transparent"}
          strokeWidth={hovered?.date === item.date ? 3 : 1}
          onMouseEnter={() => setHovered(item)}
          onMouseLeave={() => setHovered(null)}
        />
      ))}
      <text x={(margin.left + width - margin.right) / 2} y={height - 12} textAnchor="middle" className="chart-label">
        {xLabel}
      </text>
      <text x={18} y={(margin.top + height - margin.bottom) / 2} textAnchor="middle" className="chart-label" transform={`rotate(-90 18 ${(margin.top + height - margin.bottom) / 2})`}>
        {yLabel}
      </text>
      <text x={width - margin.right} y={margin.top + 16} textAnchor="end" className="chart-note">
        Hover points to see date and values. Final-exam days are outlined.
      </text>
      {hovered ? (
        <ChartTooltip
          x={x(Number(hovered[xKey]))}
          y={y(Number(hovered[yKey]))}
          lines={[
            hovered.date,
            `${xLabel}: ${Number(hovered[xKey]).toFixed(2)}`,
            `${yLabel}: ${Number(hovered[yKey]).toFixed(2)}`,
            hovered.analysisPeriod.replaceAll("_", " "),
          ]}
        />
      ) : null}
    </svg>
  );
}

export function DailyDistributionSmallMultiples({ data }: { data: ChartSeries["dailyPanel"] }) {
  const [hovered, setHovered] = useState<{ label: string; x0: number; x1: number; count: number; x: number; y: number } | null>(null);
  const width = 900;
  const height = 600;
  const margin = { top: 44, right: 28, bottom: 44, left: 62 };
  const panels = [
    { key: "youtubeWatched" as const, label: "YouTube watched", color: "#5db5f0" },
    { key: "spotifyHours" as const, label: "Spotify hours", color: "#7dd7ba" },
    { key: "netflixPrimeCount" as const, label: "Netflix + Prime", color: "#d29355" },
    { key: "platformDiversity" as const, label: "Platform diversity", color: "#f0c96a" },
  ];
  const panelWidth = (width - margin.left - margin.right - 34) / 2;
  const panelHeight = (height - margin.top - margin.bottom - 58) / 2;

  return (
    <svg className="chart-svg interactive-svg" viewBox={`0 0 ${width} ${height}`} role="img">
      <title>Daily variable distributions</title>
      {panels.map((panel, index) => {
        const col = index % 2;
        const row = Math.floor(index / 2);
        const x0 = margin.left + col * (panelWidth + 34);
        const y0 = margin.top + row * (panelHeight + 58);
        const values = data.map((item) => Number(item[panel.key]));
        const xMax = Math.max(1, d3.max(values) ?? 1);
        const x = d3.scaleLinear().domain([0, xMax]).nice().range([x0, x0 + panelWidth]);
        const bins = d3.bin().domain(x.domain() as [number, number]).thresholds(18)(values);
        const y = d3.scaleLinear().domain([0, d3.max(bins, (bin) => bin.length) ?? 1]).nice().range([y0 + panelHeight, y0]);
        return (
          <g key={panel.key}>
            <text x={x0} y={y0 - 14} className="chart-label">
              {panel.label}
            </text>
            {y.ticks(3).map((tick) => (
              <line key={`${panel.key}-${tick}`} x1={x0} x2={x0 + panelWidth} y1={y(tick)} y2={y(tick)} stroke="rgba(255,255,255,0.07)" />
            ))}
            {bins.map((bin) => (
              <rect
                key={`${panel.key}-${bin.x0}-${bin.x1}`}
                x={x(bin.x0 ?? 0) + 1}
                y={y(bin.length)}
                width={Math.max(1, x(bin.x1 ?? 0) - x(bin.x0 ?? 0) - 2)}
                height={y(0) - y(bin.length)}
                rx={4}
                fill={panel.color}
                opacity={hovered === null || (hovered.label === panel.label && hovered.x0 === bin.x0 && hovered.x1 === bin.x1) ? 0.82 : 0.25}
                stroke={hovered?.label === panel.label && hovered.x0 === bin.x0 && hovered.x1 === bin.x1 ? "#fff1cf" : "transparent"}
                strokeWidth={hovered?.label === panel.label && hovered.x0 === bin.x0 && hovered.x1 === bin.x1 ? 2 : 0}
                onMouseEnter={() =>
                  setHovered({
                    label: panel.label,
                    x0: bin.x0 ?? 0,
                    x1: bin.x1 ?? 0,
                    count: bin.length,
                    x: x(bin.x1 ?? 0),
                    y: y(bin.length),
                  })
                }
                onMouseLeave={() => setHovered(null)}
              />
            ))}
            {x.ticks(4).map((tick) => (
              <text key={`${panel.key}-x-${tick}`} x={x(tick)} y={y0 + panelHeight + 24} textAnchor="middle" className="chart-axis">
                {tick}
              </text>
            ))}
            <text x={x0} y={y0 + panelHeight + 24} textAnchor="start" className="chart-note">
              0
            </text>
          </g>
        );
      })}
      {hovered ? (
        <ChartTooltip
          x={hovered.x}
          y={hovered.y}
          lines={[hovered.label, `${hovered.x0.toFixed(2)} to ${hovered.x1.toFixed(2)}`, `${hovered.count} days`]}
        />
      ) : null}
    </svg>
  );
}

export function HourlyActivityChart({ data }: { data: ChartSeries["hourlyActivity"] }) {
  const [hovered, setHovered] = useState<{ hour: number; label: string; value: number; x: number; y: number } | null>(null);
  const width = 900;
  const height = 420;
  const margin = { top: 38, right: 28, bottom: 52, left: 72 };
  const panels = [
    { key: "youtubeWatched" as const, label: "YouTube watched records", color: "#5db5f0" },
    { key: "spotifyHours" as const, label: "Spotify listening hours", color: "#7dd7ba" },
  ];
  const panelHeight = (height - margin.top - margin.bottom - 38) / 2;
  const x = d3.scaleBand().domain(data.map((item) => String(item.hour))).range([margin.left, width - margin.right]).padding(0.18);

  return (
    <svg className="chart-svg interactive-svg" viewBox={`0 0 ${width} ${height}`} role="img">
      <title>Hourly YouTube and Spotify activity in Istanbul time</title>
      {panels.map((panel, index) => {
        const y0 = margin.top + index * (panelHeight + 38);
        const yMax = Math.max(1, d3.max(data, (item) => Number(item[panel.key])) ?? 1);
        const y = d3.scaleLinear().domain([0, yMax]).nice().range([y0 + panelHeight, y0]);
        return (
          <g key={panel.key}>
            <text x={margin.left} y={y0 - 12} className="chart-label">
              {panel.label}
            </text>
            {y.ticks(3).map((tick) => (
              <g key={`${panel.key}-${tick}`}>
                <line x1={margin.left} x2={width - margin.right} y1={y(tick)} y2={y(tick)} stroke="rgba(255,255,255,0.07)" />
                <text x={margin.left - 12} y={y(tick) + 5} textAnchor="end" className="chart-axis">
                  {tick}
                </text>
              </g>
            ))}
            {data.map((item) => {
              const xPos = x(String(item.hour)) ?? margin.left;
              const value = Number(item[panel.key]);
              return (
                <rect
                  key={`${panel.key}-${item.hour}`}
                  x={xPos}
                  y={y(value)}
                  width={x.bandwidth()}
                  height={y(0) - y(value)}
                  rx={4}
                  fill={panel.color}
                  opacity={hovered === null || (hovered.hour === item.hour && hovered.label === panel.label) ? 0.86 : 0.24}
                  stroke={hovered?.hour === item.hour && hovered.label === panel.label ? "#fff1cf" : "transparent"}
                  strokeWidth={hovered?.hour === item.hour && hovered.label === panel.label ? 2 : 0}
                  onMouseEnter={() => setHovered({ hour: item.hour, label: panel.label, value, x: xPos + x.bandwidth(), y: y(value) })}
                  onMouseLeave={() => setHovered(null)}
                />
              );
            })}
          </g>
        );
      })}
      {[0, 6, 12, 18, 23].map((hour) => (
        <text key={hour} x={(x(String(hour)) ?? margin.left) + x.bandwidth() / 2} y={height - 16} textAnchor="middle" className="chart-axis">
          {hour}:00
        </text>
      ))}
      <text x={width - margin.right} y={height - 16} textAnchor="end" className="chart-note">
        Istanbul time. Hover bars to see values.
      </text>
      {hovered ? (
        <ChartTooltip x={hovered.x} y={hovered.y} lines={[`${hovered.hour}:00`, hovered.label, hovered.value.toFixed(2)]} />
      ) : null}
    </svg>
  );
}

export function HypothesisMatrix({ results }: { results: HypothesisResult[] }) {
  return (
    <div className="matrix-grid">
      {results.map((result, index) => (
        <motion.article
          key={`${result.hypothesis}-${result.outcome}`}
          className={`matrix-card ${result.decision === "Reject H0" ? "is-rejected" : "is-not-rejected"}`}
          initial={{ opacity: 0, scale: 0.94 }}
          whileInView={{ opacity: 1, scale: 1 }}
          viewport={{ once: true }}
          transition={{ delay: index * 0.04 }}
        >
          <div className="matrix-card-top">
            <span>{result.hypothesis.split(" ")[0]}</span>
            <strong>p = {formatPValue(result.pValue)}</strong>
          </div>
          <h3>{result.outcome}</h3>
          <span className="decision-pill">{result.decision}</span>
          <p>{result.interpretation}</p>
          <div className="result-meter" aria-hidden="true">
            <span style={{ width: `${Math.max(6, Math.min(100, (1 - result.pValue) * 100))}%` }} />
          </div>
          <div className="matrix-stats">
            <span>{result.test}</span>
          </div>
          <div className="result-detail-popover">
            <strong>Numbers</strong>
            <span>statistic: {result.statistic.toFixed(4)}</span>
            <span>p-value: {formatPValue(result.pValue)}</span>
            <span>means: {result.meanGroup1.toFixed(3)} / {result.meanGroup2.toFixed(3)}</span>
            <span>medians: {result.medianGroup1.toFixed(3)} / {result.medianGroup2.toFixed(3)}</span>
            <span>n: {result.nGroup1} / {result.nGroup2}</span>
          </div>
        </motion.article>
      ))}
    </div>
  );
}
