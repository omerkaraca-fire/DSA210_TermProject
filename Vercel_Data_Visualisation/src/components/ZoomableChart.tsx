"use client";

import { type ReactNode, useState } from "react";

type ZoomableChartProps = {
  children: ReactNode;
  description?: string;
  title: string;
};

export function ZoomableChart({ children, description, title }: ZoomableChartProps) {
  const [zoom, setZoom] = useState(1);

  function changeZoom(step: number) {
    setZoom((currentZoom) => Math.min(1.6, Math.max(0.8, Number((currentZoom + step).toFixed(2)))));
  }

  return (
    <article className="zoom-chart-card">
      <div className="zoom-chart-toolbar">
        <span>{title}</span>
        <div>
          <button type="button" onClick={() => changeZoom(-0.1)} aria-label={`Zoom out ${title}`}>
            -
          </button>
          <button type="button" onClick={() => setZoom(1)}>
            {Math.round(zoom * 100)}%
          </button>
          <button type="button" onClick={() => changeZoom(0.1)} aria-label={`Zoom in ${title}`}>
            +
          </button>
        </div>
      </div>
      {description ? <p className="zoom-chart-description">{description}</p> : null}
      <div className="zoom-chart-viewport">
        <div className="zoom-chart-scale" style={{ width: `${100 * zoom}%` }}>
          {children}
        </div>
      </div>
    </article>
  );
}
