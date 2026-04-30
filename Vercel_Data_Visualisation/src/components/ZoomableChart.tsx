"use client";

import { type ReactNode } from "react";

type ZoomableChartProps = {
  children: ReactNode;
  description?: string;
  title: string;
};

export function ZoomableChart({ children, description, title }: ZoomableChartProps) {
  return (
    <article className="zoom-chart-card">
      <div className="zoom-chart-toolbar">
        <span>{title}</span>
      </div>
      {description ? <p className="zoom-chart-description">{description}</p> : null}
      <div className="zoom-chart-viewport">
        <div className="zoom-chart-scale">{children}</div>
      </div>
    </article>
  );
}
