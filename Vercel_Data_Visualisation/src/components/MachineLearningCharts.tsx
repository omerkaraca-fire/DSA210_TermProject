"use client";

import * as d3 from "d3";
import type { MachineLearningConfusionMatrix, MachineLearningPeriod } from "@/types";

const metrics = [
  { key: "precision", label: "Precision", color: "#7dd7ba" },
  { key: "recall", label: "Recall", color: "#f0c96a" },
  { key: "f1Score", label: "Macro F1", color: "#f3a35c" },
] as const;

function shortModelName(model: string) {
  return model.replace(" Classifier", "").replace(" Regression", " Reg.").replace(" Clustering", "");
}

function metricValue(value: number) {
  return value.toFixed(3);
}

function findMatrix(period: MachineLearningPeriod, model: string) {
  return period.confusionMatrices.find((matrix) => matrix.model === model);
}

function bestMetric(period: MachineLearningPeriod) {
  return period.metrics.reduce((best, current) => (current.f1Score > best.f1Score ? current : best), period.metrics[0]);
}

export function MLMetricComparisonChart({ period }: { period: MachineLearningPeriod }) {
  const width = 860;
  const height = 420;
  const margin = { top: 34, right: 28, bottom: 92, left: 68 };
  const x0 = d3
    .scaleBand()
    .domain(period.metrics.map((item) => item.model))
    .range([margin.left, width - margin.right])
    .padding(0.2);
  const x1 = d3
    .scaleBand()
    .domain(metrics.map((metric) => metric.key))
    .range([0, x0.bandwidth()])
    .padding(0.12);
  const y = d3.scaleLinear().domain([0, 1]).nice().range([height - margin.bottom, margin.top]);
  const yTicks = y.ticks(5);
  const bestModel = bestMetric(period).model;

  return (
    <svg className="chart-svg interactive-svg ml-metric-chart" viewBox={`0 0 ${width} ${height}`} role="img">
      {yTicks.map((tick) => (
        <g key={tick}>
          <line x1={margin.left} x2={width - margin.right} y1={y(tick)} y2={y(tick)} stroke="rgba(240,234,219,0.1)" />
          <text x={margin.left - 14} y={y(tick) + 5} textAnchor="end" className="chart-axis">
            {tick.toFixed(1)}
          </text>
        </g>
      ))}
      {period.metrics.map((item) => {
        const groupX = x0(item.model) ?? margin.left;
        return (
          <g key={item.model}>
            {metrics.map((metric) => {
              const value = item[metric.key];
              return (
                <rect
                  key={metric.key}
                  x={groupX + (x1(metric.key) ?? 0)}
                  y={y(value)}
                  width={x1.bandwidth()}
                  height={height - margin.bottom - y(value)}
                  rx={8}
                  fill={metric.color}
                  opacity={item.model === bestModel || metric.key !== "f1Score" ? 0.9 : 0.58}
                  stroke={item.model === bestModel && metric.key === "f1Score" ? "#fff1cf" : "transparent"}
                  strokeWidth={item.model === bestModel && metric.key === "f1Score" ? 3 : 0}
                />
              );
            })}
            <text x={groupX + x0.bandwidth() / 2} y={height - 58} textAnchor="middle" className="chart-axis ml-model-label">
              {shortModelName(item.model)}
            </text>
            <text x={groupX + x0.bandwidth() / 2} y={y(item.f1Score) - 8} textAnchor="middle" className="chart-value">
              {metricValue(item.f1Score)}
            </text>
          </g>
        );
      })}
      <text x={margin.left} y={20} className="chart-note">
        Macro precision, recall, and F1. Highlighted F1 bar marks the best model.
      </text>
      <g transform={`translate(${margin.left}, ${height - 24})`}>
        {metrics.map((metric, index) => (
          <g key={metric.key} transform={`translate(${index * 142}, 0)`}>
            <rect width={16} height={16} rx={4} fill={metric.color} />
            <text x={24} y={13} className="chart-axis">
              {metric.label}
            </text>
          </g>
        ))}
      </g>
    </svg>
  );
}

export function MLConfusionMatrixHeatmap({
  compact = false,
  matrix,
}: {
  compact?: boolean;
  matrix: MachineLearningConfusionMatrix;
}) {
  const width = compact ? 420 : 560;
  const height = compact ? 360 : 410;
  const margin = compact ? { top: 58, right: 28, bottom: 54, left: 118 } : { top: 70, right: 34, bottom: 64, left: 150 };
  const cellSize = Math.min(
    (width - margin.left - margin.right) / matrix.predictedLabels.length,
    (height - margin.top - margin.bottom) / matrix.actualLabels.length,
  );
  const values = matrix.values.flat();
  const color = d3.scaleSequential(d3.interpolateYlOrBr).domain([0, Math.max(...values, 1)]);

  return (
    <svg className="chart-svg interactive-svg ml-confusion-chart" viewBox={`0 0 ${width} ${height}`} role="img">
      <text x={margin.left + cellSize} y={24} textAnchor="middle" className="chart-note">
        Predicted label
      </text>
      <text x={20} y={margin.top + cellSize} transform={`rotate(-90 20 ${margin.top + cellSize})`} textAnchor="middle" className="chart-note">
        Actual label
      </text>
      {matrix.predictedLabels.map((label, index) => (
        <text key={label} x={margin.left + index * cellSize + cellSize / 2} y={margin.top - 16} textAnchor="middle" className="chart-axis ml-axis-label">
          {label}
        </text>
      ))}
      {matrix.actualLabels.map((label, rowIndex) => (
        <text key={label} x={margin.left - 14} y={margin.top + rowIndex * cellSize + cellSize / 2 + 5} textAnchor="end" className="chart-axis ml-axis-label">
          {label}
        </text>
      ))}
      {matrix.values.map((row, rowIndex) =>
        row.map((value, columnIndex) => {
          const fill = color(value);
          return (
            <g key={`${rowIndex}-${columnIndex}`}>
              <rect
                x={margin.left + columnIndex * cellSize}
                y={margin.top + rowIndex * cellSize}
                width={cellSize}
                height={cellSize}
                rx={compact ? 14 : 18}
                fill={fill}
                stroke="rgba(7,9,8,0.24)"
              />
              <text
                x={margin.left + columnIndex * cellSize + cellSize / 2}
                y={margin.top + rowIndex * cellSize + cellSize / 2 + 9}
                textAnchor="middle"
                className="ml-confusion-value"
              >
                {value}
              </text>
            </g>
          );
        }),
      )}
      {matrix.source === "csv" ? null : (
        <text x={margin.left} y={height - 18} className="chart-note">
          Source: {matrix.source}
        </text>
      )}
    </svg>
  );
}

export function MLBestModels({ periods }: { periods: MachineLearningPeriod[] }) {
  return (
    <div className="ml-two-column">
      {periods.map((period) => {
        const best = bestMetric(period);
        const matrix = findMatrix(period, best.model);
        return (
          <article className="ml-model-card" key={period.id}>
            <p className="eyebrow">{period.title}</p>
            <h3>{best.model}</h3>
            <p>{period.target}</p>
            <dl className="ml-metric-list">
              <div>
                <dt>Macro F1</dt>
                <dd>{metricValue(best.f1Score)}</dd>
              </div>
              <div>
                <dt>Precision</dt>
                <dd>{metricValue(best.precision)}</dd>
              </div>
              <div>
                <dt>Recall</dt>
                <dd>{metricValue(best.recall)}</dd>
              </div>
            </dl>
            {matrix ? <MLConfusionMatrixHeatmap matrix={matrix} /> : null}
          </article>
        );
      })}
    </div>
  );
}

export function MLAllModelMatrices({ periods }: { periods: MachineLearningPeriod[] }) {
  return (
    <div className="ml-period-stack">
      {periods.map((period) => (
        <article className="ml-period-panel" key={period.id}>
          <div>
            <p className="eyebrow">{period.title}</p>
            <h3>{period.target}</h3>
          </div>
          <div className="ml-model-grid">
            {period.metrics.map((metric) => {
              const matrix = findMatrix(period, metric.model);
              return (
                <article className="ml-mini-model-card" key={metric.model}>
                  <h4>{metric.model}</h4>
                  <dl className="ml-metric-list is-compact">
                    <div>
                      <dt>F1</dt>
                      <dd>{metricValue(metric.f1Score)}</dd>
                    </div>
                    <div>
                      <dt>Prec.</dt>
                      <dd>{metricValue(metric.precision)}</dd>
                    </div>
                    <div>
                      <dt>Rec.</dt>
                      <dd>{metricValue(metric.recall)}</dd>
                    </div>
                  </dl>
                  {matrix ? <MLConfusionMatrixHeatmap compact matrix={matrix} /> : null}
                </article>
              );
            })}
          </div>
        </article>
      ))}
    </div>
  );
}
