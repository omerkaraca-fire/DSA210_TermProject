"use client";

import * as d3 from "d3";
import { motion } from "framer-motion";
import { useMemo, useState } from "react";
import type { BoxPlotDatum, ChartSeries } from "@/types";

type BarDatum = {
  label: string;
  value: number;
};

type MonthlyDatum = {
  month: string;
  [key: string]: number | string;
};

type SeriesDefinition = {
  key: string;
  label: string;
  color: string;
  unit: string;
};

function niceValue(value: number) {
  if (Number.isInteger(value)) {
    return value.toLocaleString("en-US");
  }
  if (Math.abs(value) >= 100) {
    return Math.round(value).toLocaleString("en-US");
  }
  if (Math.abs(value) >= 10) {
    return value.toFixed(1);
  }
  return value.toFixed(2);
}

function TooltipBox({ x, y, lines }: { x: number; y: number; lines: string[] }) {
  const width = Math.max(170, Math.max(...lines.map((line) => line.length)) * 7.5);
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

export function AnimatedPipeline() {
  const steps = [
    ["Raw exports", "Platform files with different structures"],
    ["Processing", "Normalize dates, mask identifiers"],
    ["Public tables", "Keep useful behavior fields only"],
    ["Daily EDA", "Aggregate by date and academic period"],
    ["Tests", "Run simple nonparametric checks"],
  ];

  return (
    <div className="animated-pipeline">
      <svg viewBox="0 0 980 250" className="chart-svg" role="img">
        <title>Animated processing pipeline from exports to tests</title>
        <defs>
          <linearGradient id="warm-flow-gradient" x1="0%" x2="100%" y1="0%" y2="0%">
            <stop offset="0%" stopColor="#f3a35c" />
            <stop offset="45%" stopColor="#ffd08a" />
            <stop offset="100%" stopColor="#9ed8b3" />
          </linearGradient>
        </defs>
        <motion.path
          d="M 75 178 C 220 142, 350 218, 490 178 S 760 134, 905 178"
          fill="none"
          stroke="url(#warm-flow-gradient)"
          strokeLinecap="round"
          strokeWidth="4"
          opacity="0.82"
          initial={{ pathLength: 0 }}
          animate={{ pathLength: 1 }}
          transition={{ duration: 4.5, repeat: Infinity, repeatType: "reverse", ease: "easeInOut" }}
        />
        {steps.map((step, index) => {
          const x = 55 + index * 218;
          const y = 48;
          return (
            <g key={step[0]}>
              <rect x={x} y={y} width={150} height={76} rx={22} className="pipeline-node" />
              <text x={x + 75} y={y + 30} textAnchor="middle" className="chart-label">
                {step[0]}
              </text>
              <foreignObject x={x + 14} y={y + 38} width={122} height={32}>
                <p className="diagram-note">{step[1]}</p>
              </foreignObject>
            </g>
          );
        })}
      </svg>
    </div>
  );
}

export function InteractiveBarChart({
  data,
  title,
  unit,
  color = "#f3a35c",
  horizontal = false,
}: {
  data: BarDatum[];
  title: string;
  unit: string;
  color?: string;
  horizontal?: boolean;
}) {
  const [hovered, setHovered] = useState<number | null>(null);
  const width = 900;
  const height = horizontal ? 520 : 380;
  const margin = horizontal
    ? { top: 42, right: 42, bottom: 44, left: 190 }
    : { top: 42, right: 38, bottom: 84, left: 78 };
  const maxValue = Math.max(1, d3.max(data, (item) => item.value) ?? 1);

  if (horizontal) {
    const y = d3.scaleBand().domain(data.map((item) => item.label)).range([margin.top, height - margin.bottom]).padding(0.24);
    const x = d3.scaleLinear().domain([0, maxValue]).nice().range([margin.left, width - margin.right]);
    const hoveredDatum = hovered === null ? null : data[hovered];
    return (
      <svg className="chart-svg interactive-svg" viewBox={`0 0 ${width} ${height}`} role="img">
        <title>{title}</title>
        <text x={margin.left} y={24} className="chart-label">
          {title}
        </text>
        {x.ticks(5).map((tick) => (
          <line key={tick} x1={x(tick)} x2={x(tick)} y1={margin.top} y2={height - margin.bottom} stroke="rgba(255,255,255,0.07)" />
        ))}
        {data.map((item, index) => {
          const yPos = y(item.label) ?? 0;
          const isHovered = hovered === index;
          return (
            <g key={item.label} onMouseEnter={() => setHovered(index)} onMouseLeave={() => setHovered(null)}>
              <text x={margin.left - 12} y={yPos + y.bandwidth() / 2 + 5} textAnchor="end" className="chart-axis">
                {item.label.length > 22 ? `${item.label.slice(0, 22)}...` : item.label}
              </text>
              <rect
                x={margin.left}
                y={yPos}
                width={x(item.value) - margin.left}
                height={y.bandwidth()}
                rx={10}
                fill={color}
                opacity={hovered === null || isHovered ? 0.95 : 0.28}
                stroke={isHovered ? "#fff1cf" : "transparent"}
                strokeWidth={isHovered ? 3 : 0}
              />
              <text x={x(item.value) + 8} y={yPos + y.bandwidth() / 2 + 5} className="chart-value">
                {niceValue(item.value)}
              </text>
            </g>
          );
        })}
        {hoveredDatum ? <TooltipBox x={x(hoveredDatum.value)} y={y(hoveredDatum.label) ?? margin.top} lines={[hoveredDatum.label, `${niceValue(hoveredDatum.value)} ${unit}`]} /> : null}
      </svg>
    );
  }

  const x = d3.scaleBand().domain(data.map((item) => item.label)).range([margin.left, width - margin.right]).padding(0.25);
  const y = d3.scaleLinear().domain([0, maxValue]).nice().range([height - margin.bottom, margin.top]);
  const hoveredDatum = hovered === null ? null : data[hovered];
  const hoveredX = hoveredDatum ? (x(hoveredDatum.label) ?? margin.left) + x.bandwidth() / 2 : 0;
  const hoveredY = hoveredDatum ? y(hoveredDatum.value) : 0;
  const labelStep = data.length > 18 ? 4 : data.length > 12 ? 2 : 1;

  return (
    <svg className="chart-svg interactive-svg" viewBox={`0 0 ${width} ${height}`} role="img">
      <title>{title}</title>
      <text x={margin.left} y={24} className="chart-label">
        {title}
      </text>
      {y.ticks(5).map((tick) => (
        <g key={tick}>
          <line x1={margin.left} x2={width - margin.right} y1={y(tick)} y2={y(tick)} stroke="rgba(255,255,255,0.07)" />
          <text x={margin.left - 12} y={y(tick) + 5} textAnchor="end" className="chart-axis">
            {tick}
          </text>
        </g>
      ))}
      {data.map((item, index) => {
        const xPos = x(item.label) ?? 0;
        const isHovered = hovered === index;
        return (
          <g key={item.label} onMouseEnter={() => setHovered(index)} onMouseLeave={() => setHovered(null)}>
            <rect
              x={xPos}
              y={y(item.value)}
              width={x.bandwidth()}
              height={height - margin.bottom - y(item.value)}
              rx={12}
              fill={color}
              opacity={hovered === null || isHovered ? 0.95 : 0.28}
              stroke={isHovered ? "#fff1cf" : "transparent"}
              strokeWidth={isHovered ? 3 : 0}
            />
            {index % labelStep === 0 || index === data.length - 1 ? (
              <text x={xPos + x.bandwidth() / 2} y={height - 44} textAnchor="middle" className="chart-axis">
                {item.label.length > 12 ? `${item.label.slice(0, 12)}...` : item.label}
              </text>
            ) : null}
          </g>
        );
      })}
      {hoveredDatum ? <TooltipBox x={hoveredX} y={hoveredY} lines={[hoveredDatum.label, `${niceValue(hoveredDatum.value)} ${unit}`]} /> : null}
    </svg>
  );
}

export function InteractiveMonthlyLines({
  data,
  title,
  series,
}: {
  data: MonthlyDatum[];
  title: string;
  series: SeriesDefinition[];
}) {
  const [hovered, setHovered] = useState<{ row: MonthlyDatum; series: SeriesDefinition } | null>(null);
  const width = 900;
  const height = 440;
  const margin = { top: 54, right: 34, bottom: 54, left: 82 };
  const dates = data.map((item) => new Date(item.month));
  const x = d3.scaleTime().domain(d3.extent(dates) as [Date, Date]).range([margin.left, width - margin.right]);
  const maxValue = Math.max(1, d3.max(data, (item) => d3.max(series, (entry) => Number(item[entry.key]))) ?? 1);
  const y = d3.scaleLinear().domain([0, maxValue]).nice().range([height - margin.bottom, margin.top]);
  const paths = useMemo(
    () =>
      series.map((entry) => ({
        ...entry,
        path: d3
          .line<MonthlyDatum>()
          .x((item) => x(new Date(item.month)))
          .y((item) => y(Number(item[entry.key])))
          .curve(d3.curveCatmullRom.alpha(0.45))(data),
      })),
    [data, series, x, y],
  );

  return (
    <svg className="chart-svg interactive-svg" viewBox={`0 0 ${width} ${height}`} role="img">
      <title>{title}</title>
      <text x={margin.left} y={30} className="chart-label">
        {title}
      </text>
      {y.ticks(5).map((tick) => (
        <g key={tick}>
          <line x1={margin.left} x2={width - margin.right} y1={y(tick)} y2={y(tick)} stroke="rgba(255,255,255,0.07)" />
          <text x={margin.left - 12} y={y(tick) + 5} textAnchor="end" className="chart-axis">
            {tick}
          </text>
        </g>
      ))}
      {x.ticks(6).map((tick) => (
        <text key={tick.toISOString()} x={x(tick)} y={height - 18} textAnchor="middle" className="chart-axis">
          {tick.getFullYear()}
        </text>
      ))}
      {paths.map((entry) => (
        <path key={entry.key} d={entry.path ?? ""} fill="none" stroke={entry.color} strokeWidth={4} opacity={hovered && hovered.series.key !== entry.key ? 0.22 : 0.95} />
      ))}
      {series.map((entry, seriesIndex) => (
        <g key={`points-${entry.key}`}>
          {data.map((item) => {
            const value = Number(item[entry.key]);
            const isHovered = hovered?.row.month === item.month && hovered.series.key === entry.key;
            return (
              <circle
                key={`${entry.key}-${item.month}`}
                cx={x(new Date(item.month))}
                cy={y(value)}
                r={isHovered ? 7 : 4}
                fill={entry.color}
                opacity={hovered && !isHovered ? 0.22 : 0.95}
                stroke={isHovered ? "#fff1cf" : "#15100d"}
                strokeWidth={isHovered ? 3 : 1}
                onMouseEnter={() => setHovered({ row: item, series: entry })}
                onMouseLeave={() => setHovered(null)}
              />
            );
          })}
          <circle cx={margin.left + seriesIndex * 210} cy={height - 18} r={6} fill={entry.color} />
          <text x={margin.left + 12 + seriesIndex * 210} y={height - 14} className="chart-note">
            {entry.label}
          </text>
        </g>
      ))}
      {hovered ? (
        <TooltipBox
          x={x(new Date(hovered.row.month))}
          y={y(Number(hovered.row[hovered.series.key]))}
          lines={[
            hovered.row.month.slice(0, 7),
            hovered.series.label,
            `${niceValue(Number(hovered.row[hovered.series.key]))} ${hovered.series.unit}`,
          ]}
        />
      ) : null}
    </svg>
  );
}

export function InteractiveBoxPlot({
  data,
  title,
  unit,
  color = "#f3a35c",
}: {
  data: BoxPlotDatum[];
  title: string;
  unit: string;
  color?: string;
}) {
  const [hovered, setHovered] = useState<BoxPlotDatum | null>(null);
  const width = 900;
  const height = 420;
  const margin = { top: 54, right: 38, bottom: 86, left: 82 };
  const maxValue = Math.max(1, d3.max(data, (item) => item.max) ?? 1);
  const x = d3.scaleBand().domain(data.map((item) => item.label)).range([margin.left, width - margin.right]).padding(0.32);
  const y = d3.scaleLinear().domain([0, maxValue]).nice().range([height - margin.bottom, margin.top]);
  const labelStep = data.length > 8 ? 2 : 1;

  return (
    <svg className="chart-svg interactive-svg" viewBox={`0 0 ${width} ${height}`} role="img">
      <title>{title}</title>
      <text x={margin.left} y={28} className="chart-label">
        {title}
      </text>
      {y.ticks(5).map((tick) => (
        <g key={tick}>
          <line x1={margin.left} x2={width - margin.right} y1={y(tick)} y2={y(tick)} stroke="rgba(255,255,255,0.07)" />
          <text x={margin.left - 12} y={y(tick) + 5} textAnchor="end" className="chart-axis">
            {tick}
          </text>
        </g>
      ))}
      {data.map((item, index) => {
        const xPos = x(item.label) ?? 0;
        const midX = xPos + x.bandwidth() / 2;
        const isHovered = hovered?.label === item.label;
        const label = item.label.length > 14 ? `${item.label.slice(0, 14)}...` : item.label;
        const boxHeight = Math.max(2, y(item.q1) - y(item.q3));
        const isFlatBox = item.q1 === item.q3;
        return (
          <g key={item.label} onMouseEnter={() => setHovered(item)} onMouseLeave={() => setHovered(null)}>
            <line
              x1={midX}
              x2={midX}
              y1={y(item.min)}
              y2={y(item.max)}
              stroke={color}
              strokeWidth={isHovered ? 5 : 3}
              opacity={hovered === null || isHovered ? 0.95 : 0.28}
            />
            <line x1={midX - x.bandwidth() * 0.25} x2={midX + x.bandwidth() * 0.25} y1={y(item.min)} y2={y(item.min)} stroke={color} strokeWidth={3} />
            <line x1={midX - x.bandwidth() * 0.25} x2={midX + x.bandwidth() * 0.25} y1={y(item.max)} y2={y(item.max)} stroke={color} strokeWidth={3} />
            <rect
              x={xPos}
              y={y(item.q3)}
              width={x.bandwidth()}
              height={boxHeight}
              rx={10}
              fill={color}
              opacity={hovered === null || isHovered ? (isFlatBox ? 0.42 : 0.72) : 0.22}
              stroke={isHovered ? "#fff1cf" : "transparent"}
              strokeWidth={isHovered ? 3 : 0}
            />
            <line x1={xPos} x2={xPos + x.bandwidth()} y1={y(item.median)} y2={y(item.median)} stroke="#fff1cf" strokeWidth={3} />
            <circle
              cx={midX}
              cy={y(item.mean)}
              r={isHovered ? 7 : 5}
              fill="#fff1cf"
              stroke={color}
              strokeWidth={3}
              opacity={hovered === null || isHovered ? 0.95 : 0.25}
            />
            {index % labelStep === 0 || index === data.length - 1 ? (
              <text x={midX} y={height - 42} textAnchor="middle" className="chart-axis">
                {label}
              </text>
            ) : null}
          </g>
        );
      })}
      <text x={width - margin.right} y={height - 18} textAnchor="end" className="chart-note">
        Box = Q1-Q3, line = median, whiskers = min/max.
      </text>
      {hovered ? (
        <TooltipBox
          x={(x(hovered.label) ?? margin.left) + x.bandwidth()}
          y={y(hovered.median)}
          lines={[
            hovered.label,
            `median: ${niceValue(hovered.median)} ${unit}`,
            `mean: ${niceValue(hovered.mean)} ${unit}`,
            `Q1-Q3: ${niceValue(hovered.q1)}-${niceValue(hovered.q3)}`,
            `active days: ${hovered.activeCount}/${hovered.count}`,
            `n = ${hovered.count}`,
          ]}
        />
      ) : null}
    </svg>
  );
}

export function SparseActivityChart({
  data,
  title,
  unit,
  color = "#d78355",
}: {
  data: BoxPlotDatum[];
  title: string;
  unit: string;
  color?: string;
}) {
  const [hovered, setHovered] = useState<BoxPlotDatum | null>(null);
  const width = 900;
  const height = 390;
  const margin = { top: 56, right: 40, bottom: 76, left: 82 };
  const maxValue = Math.max(1, d3.max(data, (item) => item.activeCount) ?? 1);
  const x = d3.scaleBand().domain(data.map((item) => item.label)).range([margin.left, width - margin.right]).padding(0.28);
  const y = d3.scaleLinear().domain([0, maxValue]).nice().range([height - margin.bottom, margin.top]);

  return (
    <svg className="chart-svg interactive-svg" viewBox={`0 0 ${width} ${height}`} role="img">
      <title>{title}</title>
      <text x={margin.left} y={28} className="chart-label">
        {title}
      </text>
      <text x={width - margin.right} y={28} textAnchor="end" className="chart-note">
        Zero days excluded. Bars = active days; avg = records per active day.
      </text>
      {y.ticks(5).map((tick) => (
        <g key={tick}>
          <line x1={margin.left} x2={width - margin.right} y1={y(tick)} y2={y(tick)} stroke="rgba(255,255,255,0.07)" />
          <text x={margin.left - 12} y={y(tick) + 5} textAnchor="end" className="chart-axis">
            {tick}
          </text>
        </g>
      ))}
      {data.map((item) => {
        const xPos = x(item.label) ?? 0;
        const isHovered = hovered?.label === item.label;
        return (
          <g key={item.label} onMouseEnter={() => setHovered(item)} onMouseLeave={() => setHovered(null)}>
            <rect
              x={xPos}
              y={y(item.activeCount)}
              width={x.bandwidth()}
              height={height - margin.bottom - y(item.activeCount)}
              rx={12}
              fill={color}
              opacity={hovered === null || isHovered ? 0.88 : 0.28}
              stroke={isHovered ? "#fff1cf" : "transparent"}
              strokeWidth={isHovered ? 3 : 0}
            />
            <text x={xPos + x.bandwidth() / 2} y={y(item.activeCount) - 10} textAnchor="middle" className="chart-value">
              {item.activeCount}
            </text>
            <text x={xPos + x.bandwidth() / 2} y={height - 44} textAnchor="middle" className="chart-axis">
              {item.label}
            </text>
            <text x={xPos + x.bandwidth() / 2} y={height - 22} textAnchor="middle" className="chart-note">
              avg {niceValue(item.activeMean)}
            </text>
          </g>
        );
      })}
      <text x={margin.left - 52} y={margin.top - 14} className="chart-note">
        active days
      </text>
      {hovered ? (
        <TooltipBox
          x={(x(hovered.label) ?? margin.left) + x.bandwidth()}
          y={y(hovered.activeCount)}
          lines={[
            hovered.label,
            `active days: ${hovered.activeCount}/${hovered.count}`,
            `active-day mean: ${niceValue(hovered.activeMean)} ${unit}`,
            `active-day median: ${niceValue(hovered.activeMedian)} ${unit}`,
            `max: ${niceValue(hovered.max)} ${unit}`,
          ]}
        />
      ) : null}
    </svg>
  );
}

export function InteractiveDailyScatter({
  data,
  xKey,
  yKey,
  xLabel,
  yLabel,
  color,
}: {
  data: ChartSeries["dailyPanel"];
  xKey: keyof ChartSeries["dailyPanel"][number];
  yKey: keyof ChartSeries["dailyPanel"][number];
  xLabel: string;
  yLabel: string;
  color: string;
}) {
  const [hovered, setHovered] = useState<ChartSeries["dailyPanel"][number] | null>(null);
  const width = 900;
  const height = 520;
  const margin = { top: 46, right: 42, bottom: 70, left: 84 };
  const xMax = Math.max(1, d3.max(data, (item) => Number(item[xKey])) ?? 1);
  const yMax = Math.max(1, d3.max(data, (item) => Number(item[yKey])) ?? 1);
  const x = d3.scaleLinear().domain([0, xMax]).nice().range([margin.left, width - margin.right]);
  const y = d3.scaleLinear().domain([0, yMax]).nice().range([height - margin.bottom, margin.top]);

  return (
    <svg className="chart-svg interactive-svg" viewBox={`0 0 ${width} ${height}`} role="img">
      <title>{`${yLabel} by ${xLabel}`}</title>
      {x.ticks(5).map((tick) => (
        <g key={`x-${tick}`}>
          <line x1={x(tick)} x2={x(tick)} y1={margin.top} y2={height - margin.bottom} stroke="rgba(255,255,255,0.06)" />
          <text x={x(tick)} y={height - 32} textAnchor="middle" className="chart-axis">
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
      {data.map((item) => {
        const isHovered = hovered?.date === item.date;
        return (
          <circle
            key={item.date}
            cx={x(Number(item[xKey]))}
            cy={y(Number(item[yKey]))}
            r={isHovered ? 7 : 4}
            fill={color}
            opacity={hovered === null || isHovered ? 0.78 : 0.13}
            stroke={isHovered || item.analysisPeriod === "final_exam" ? "#fff1cf" : "transparent"}
            strokeWidth={isHovered ? 3 : 1}
            onMouseEnter={() => setHovered(item)}
            onMouseLeave={() => setHovered(null)}
          />
        );
      })}
      <text x={(margin.left + width - margin.right) / 2} y={height - 12} textAnchor="middle" className="chart-label">
        {xLabel}
      </text>
      <text x={18} y={(margin.top + height - margin.bottom) / 2} textAnchor="middle" className="chart-label" transform={`rotate(-90 18 ${(margin.top + height - margin.bottom) / 2})`}>
        {yLabel}
      </text>
      {hovered ? (
        <TooltipBox
          x={x(Number(hovered[xKey]))}
          y={y(Number(hovered[yKey]))}
          lines={[
            hovered.date,
            `${xLabel}: ${niceValue(Number(hovered[xKey]))}`,
            `${yLabel}: ${niceValue(Number(hovered[yKey]))}`,
            hovered.analysisPeriod.replaceAll("_", " "),
          ]}
        />
      ) : null}
    </svg>
  );
}

export function InteractiveHeatmap({ data }: { data: ChartSeries["correlation"] }) {
  const [hovered, setHovered] = useState<{ row: number; column: number; value: number } | null>(null);
  const width = 900;
  const height = 760;
  const margin = { top: 150, right: 34, bottom: 40, left: 220 };
  const labels = data.labels;
  const cell = Math.min((width - margin.left - margin.right) / labels.length, (height - margin.top - margin.bottom) / labels.length);
  const color = d3.scaleSequential((value: number) => d3.interpolateRdBu(1 - value)).domain([-1, 1]);

  return (
    <svg className="chart-svg interactive-svg" viewBox={`0 0 ${width} ${height}`} role="img">
      <title>Interactive Spearman correlation heatmap</title>
      {labels.map((label, index) => (
        <g key={label}>
          <text
            x={margin.left + index * cell + cell / 2}
            y={margin.top - 14}
            textAnchor="end"
            className="chart-axis heatmap-axis"
            transform={`rotate(-45 ${margin.left + index * cell + cell / 2} ${margin.top - 14})`}
          >
            {label}
          </text>
          <text x={margin.left - 12} y={margin.top + index * cell + cell / 2 + 5} textAnchor="end" className="chart-axis heatmap-axis">
            {label}
          </text>
        </g>
      ))}
      {data.matrix.map((row, rowIndex) =>
        row.map((value, columnIndex) => {
          const isHovered = hovered?.row === rowIndex && hovered.column === columnIndex;
          return (
            <g key={`${rowIndex}-${columnIndex}`} onMouseEnter={() => setHovered({ row: rowIndex, column: columnIndex, value })} onMouseLeave={() => setHovered(null)}>
              <rect
                x={margin.left + columnIndex * cell}
                y={margin.top + rowIndex * cell}
                width={cell - 2}
                height={cell - 2}
                rx={8}
                fill={color(value)}
                opacity={hovered === null || isHovered ? 0.95 : 0.34}
                stroke={isHovered ? "#fff1cf" : "transparent"}
                strokeWidth={isHovered ? 3 : 0}
              />
              <text x={margin.left + columnIndex * cell + cell / 2} y={margin.top + rowIndex * cell + cell / 2 + 5} textAnchor="middle" className="heatmap-value">
                {value.toFixed(2)}
              </text>
            </g>
          );
        }),
      )}
      {hovered ? (
        <TooltipBox
          x={margin.left + hovered.column * cell + cell}
          y={margin.top + hovered.row * cell}
          lines={[labels[hovered.row], labels[hovered.column], `rho = ${hovered.value.toFixed(2)}`]}
        />
      ) : null}
    </svg>
  );
}
