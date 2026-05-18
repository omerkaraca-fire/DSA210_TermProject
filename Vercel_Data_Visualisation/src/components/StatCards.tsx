import type { DatasetSummary, HypothesisResult } from "@/types";
import { formatNumber, formatPValue } from "@/lib/data";
import type { CSSProperties } from "react";

export function DatasetCards({ datasets }: { datasets: DatasetSummary[] }) {
  return (
    <div className="card-grid">
      {datasets.map((dataset) => (
        <article key={dataset.id} className="data-card" style={{ "--accent": dataset.color } as CSSProperties}>
          <span className="card-kicker">{dataset.role}</span>
          <h3>{dataset.name}</h3>
          <strong>{dataset.rowCount.toLocaleString("en-US")} rows</strong>
          <p>
            {dataset.dateStart} to {dataset.dateEnd}
          </p>
          <small>{dataset.notes}</small>
        </article>
      ))}
    </div>
  );
}

export function HypothesisResultCards({ results }: { results: HypothesisResult[] }) {
  return (
    <div className="result-card-grid">
      {results.map((result) => (
        <article
          className={`result-card ${result.decision === "Reject H0" ? "is-rejected" : "is-not-rejected"}`}
          key={`${result.hypothesis}-${result.outcome}`}
        >
          <div className="result-card-header">
            <span>{result.hypothesis.split(" ")[0]}</span>
            <strong>p = {formatPValue(result.pValue)}</strong>
          </div>
          <span className="decision-pill">{result.decision}</span>
          <h3>{result.outcome}</h3>
          <p>{result.interpretation}</p>
          <div className="result-meter" aria-hidden="true">
            <span style={{ width: `${Math.max(6, Math.min(100, (1 - result.pValue) * 100))}%` }} />
          </div>
          <dl>
            <div>
              <dt>statistic</dt>
              <dd>{formatNumber(result.statistic)}</dd>
            </div>
            <div>
              <dt>test</dt>
              <dd>{result.test}</dd>
            </div>
          </dl>
          <div className="result-detail-popover">
            <strong>Numbers</strong>
            <span>statistic: {formatNumber(result.statistic)}</span>
            <span>p-value: {formatPValue(result.pValue)}</span>
            <span>means: {formatNumber(result.meanGroup1)} / {formatNumber(result.meanGroup2)}</span>
            <span>medians: {formatNumber(result.medianGroup1)} / {formatNumber(result.medianGroup2)}</span>
            <span>n: {result.nGroup1} / {result.nGroup2}</span>
          </div>
        </article>
      ))}
    </div>
  );
}
