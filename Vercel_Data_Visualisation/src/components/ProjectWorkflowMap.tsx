"use client";

import { useMemo, useState } from "react";
import type { CSSProperties } from "react";

const CANVAS_WIDTH = 1400;
const CANVAS_HEIGHT = 650;

type WorkflowTone = "source" | "prep" | "eda" | "hypothesis" | "ml" | "output";
type AnchorSide = "left" | "right" | "top" | "bottom";

type WorkflowNode = {
  id: string;
  title: string;
  eyebrow: string;
  text: string;
  tone: WorkflowTone;
  tags: string[];
  x: number;
  y: number;
  w: number;
  h: number;
};

type WorkflowEdge = {
  from: string;
  to: string;
  fromSide: AnchorSide;
  toSide: AnchorSide;
  tone: WorkflowTone;
};

type WorkflowZone = {
  label: string;
  x: number;
  y: number;
  w: number;
  h: number;
};

const WORKFLOW_NODES: WorkflowNode[] = [
  {
    id: "youtube",
    title: "YouTube",
    eyebrow: "Raw export",
    text: "Google Takeout activity records with watch/search events and timestamps.",
    tone: "source",
    tags: ["Watch", "Search", "Time"],
    x: 78,
    y: 120,
    w: 155,
    h: 76,
  },
  {
    id: "spotify",
    title: "Spotify",
    eyebrow: "Raw export",
    text: "Streaming-history JSON with track metadata, timestamps, and listening duration.",
    tone: "source",
    tags: ["Hours", "Streams", "Tracks"],
    x: 78,
    y: 226,
    w: 155,
    h: 76,
  },
  {
    id: "streaming",
    title: "Netflix + Prime",
    eyebrow: "Raw export",
    text: "Long-form viewing records from Netflix and Prime Video.",
    tone: "source",
    tags: ["Series", "Movies"],
    x: 78,
    y: 332,
    w: 155,
    h: 76,
  },
  {
    id: "calendar",
    title: "Academic Calendar",
    eyebrow: "Label source",
    text: "Calendar labels define ordinary term, final exam, and summer work periods.",
    tone: "source",
    tags: ["Periods", "Labels"],
    x: 78,
    y: 438,
    w: 155,
    h: 76,
  },
  {
    id: "public-tables",
    title: "Public Tables",
    eyebrow: "Preparation",
    text: "Raw files are normalized, privacy-sensitive fields are reduced, and shared date fields are created.",
    tone: "prep",
    tags: ["Clean", "Mask", "Align"],
    x: 332,
    y: 178,
    w: 160,
    h: 88,
  },
  {
    id: "daily-panel",
    title: "Daily Panel",
    eyebrow: "Preparation",
    text: "Platform rows are aggregated by date and merged with academic-period labels.",
    tone: "prep",
    tags: ["Daily", "Merge", "Features"],
    x: 332,
    y: 356,
    w: 160,
    h: 88,
  },
  {
    id: "individual-eda",
    title: "Individual EDA",
    eyebrow: "Exploration",
    text: "Each platform is inspected separately for activity volume, timing, and repeated behavior.",
    tone: "eda",
    tags: ["Platform", "Trends"],
    x: 575,
    y: 178,
    w: 150,
    h: 88,
  },
  {
    id: "combined-eda",
    title: "Combined EDA",
    eyebrow: "Exploration",
    text: "Daily platform variables are compared across academic periods and against each other.",
    tone: "eda",
    tags: ["Periods", "Correlations"],
    x: 575,
    y: 356,
    w: 150,
    h: 88,
  },
  {
    id: "rank-tests",
    title: "Rank Tests",
    eyebrow: "Hypothesis testing",
    text: "Mann-Whitney U tests compare final-exam and ordinary-term behavior, plus long-form active days.",
    tone: "hypothesis",
    tags: ["H1", "H2", "H3", "H5"],
    x: 805,
    y: 178,
    w: 155,
    h: 88,
  },
  {
    id: "spearman",
    title: "Co-Usage Test",
    eyebrow: "Hypothesis testing",
    text: "Spearman correlation checks whether Spotify hours and YouTube watched count move together.",
    tone: "hypothesis",
    tags: ["H4", "rho"],
    x: 805,
    y: 356,
    w: 155,
    h: 88,
  },
  {
    id: "binary-ml",
    title: "Binary ML",
    eyebrow: "Machine learning",
    text: "Models classify final vs ordinary and summer work vs ordinary using daily entertainment features.",
    tone: "ml",
    tags: ["Final", "Summer"],
    x: 1032,
    y: 178,
    w: 160,
    h: 88,
  },
  {
    id: "all-ml",
    title: "All-Period ML",
    eyebrow: "Machine learning",
    text: "A three-class task predicts ordinary term, final exam, and summer work period together.",
    tone: "ml",
    tags: ["3 classes", "Macro F1"],
    x: 1032,
    y: 356,
    w: 160,
    h: 88,
  },
  {
    id: "webapp",
    title: "Vercel Web App",
    eyebrow: "Output",
    text: "The website presents the cleaned data story, EDA graphics, hypothesis results, and ML outputs.",
    tone: "output",
    tags: ["Interactive", "Public"],
    x: 1246,
    y: 214,
    w: 118,
    h: 90,
  },
  {
    id: "report",
    title: "Final Report",
    eyebrow: "Output",
    text: "The written report summarizes motivation, data sources, methods, findings, limitations, and appendix figures.",
    tone: "output",
    tags: ["PDF", "Appendix"],
    x: 1246,
    y: 366,
    w: 118,
    h: 90,
  },
];

const WORKFLOW_EDGES: WorkflowEdge[] = [
  { from: "youtube", to: "public-tables", fromSide: "right", toSide: "left", tone: "source" },
  { from: "spotify", to: "public-tables", fromSide: "right", toSide: "left", tone: "source" },
  { from: "streaming", to: "public-tables", fromSide: "right", toSide: "left", tone: "source" },
  { from: "calendar", to: "daily-panel", fromSide: "right", toSide: "left", tone: "source" },
  { from: "public-tables", to: "daily-panel", fromSide: "bottom", toSide: "top", tone: "prep" },
  { from: "daily-panel", to: "individual-eda", fromSide: "right", toSide: "left", tone: "eda" },
  { from: "daily-panel", to: "combined-eda", fromSide: "right", toSide: "left", tone: "eda" },
  { from: "individual-eda", to: "rank-tests", fromSide: "right", toSide: "left", tone: "hypothesis" },
  { from: "combined-eda", to: "rank-tests", fromSide: "right", toSide: "left", tone: "hypothesis" },
  { from: "combined-eda", to: "spearman", fromSide: "right", toSide: "left", tone: "hypothesis" },
  { from: "daily-panel", to: "binary-ml", fromSide: "right", toSide: "left", tone: "ml" },
  { from: "daily-panel", to: "all-ml", fromSide: "right", toSide: "left", tone: "ml" },
  { from: "rank-tests", to: "report", fromSide: "right", toSide: "left", tone: "output" },
  { from: "spearman", to: "report", fromSide: "right", toSide: "left", tone: "output" },
  { from: "binary-ml", to: "webapp", fromSide: "right", toSide: "left", tone: "output" },
  { from: "all-ml", to: "webapp", fromSide: "right", toSide: "left", tone: "output" },
  { from: "binary-ml", to: "report", fromSide: "right", toSide: "left", tone: "output" },
  { from: "all-ml", to: "report", fromSide: "right", toSide: "left", tone: "output" },
];

const ZONES: WorkflowZone[] = [
  { label: "Data Sources", x: 36, y: 70, w: 238, h: 500 },
  { label: "Public Prep", x: 300, y: 70, w: 220, h: 500 },
  { label: "EDA", x: 545, y: 70, w: 205, h: 500 },
  { label: "Hypothesis Tests", x: 775, y: 70, w: 215, h: 500 },
  { label: "Machine Learning", x: 1008, y: 70, w: 210, h: 500 },
  { label: "Outputs", x: 1234, y: 70, w: 145, h: 500 },
];

export function ProjectWorkflowMap() {
  const [activeId, setActiveId] = useState<string | null>(null);
  const nodeMap = useMemo(() => new Map(WORKFLOW_NODES.map((node) => [node.id, node])), []);
  const activeNode = activeId ? nodeMap.get(activeId) ?? null : null;
  const popupStyle = activeNode ? getPopupStyle(activeNode) : undefined;

  return (
    <section className="project-workflow" aria-labelledby="workflow-title">
      <div className="project-workflow-head">
        <p className="eyebrow">Project workflow</p>
        <h2 id="workflow-title">From platform exports to EDA, tests, ML, and public outputs.</h2>
        <p>
          This map shows the main path of the project: personal platform exports are reduced into public
          tables, aggregated into a daily panel, inspected with EDA, tested with hypotheses, modeled with
          machine learning, and then summarized in the website and final report.
        </p>
      </div>

      <div className="project-workflow-shell">
        <div className="project-workflow-map" aria-label="DSA210 project workflow map">
          <svg
            className="project-workflow-svg"
            viewBox={`0 0 ${CANVAS_WIDTH} ${CANVAS_HEIGHT}`}
            preserveAspectRatio="none"
            aria-hidden="true"
          >
            {ZONES.map((zone) => (
              <g key={zone.label} className="project-workflow-zone">
                <rect x={zone.x} y={zone.y} width={zone.w} height={zone.h} rx="22" />
                <text x={zone.x + 18} y={zone.y + 32}>
                  {zone.label}
                </text>
              </g>
            ))}
            {WORKFLOW_EDGES.map((edge, index) => {
              const from = nodeMap.get(edge.from);
              const to = nodeMap.get(edge.to);
              if (!from || !to) return null;
              return (
                <path
                  key={`${edge.from}-${edge.to}`}
                  className={`project-flow-path path-${index % 6} is-${edge.tone}`}
                  d={buildEdgePath(from, to, edge)}
                />
              );
            })}
          </svg>

          {WORKFLOW_NODES.map((node) => {
            const style = {
              left: `${(node.x / CANVAS_WIDTH) * 100}%`,
              top: `${(node.y / CANVAS_HEIGHT) * 100}%`,
              width: `${(node.w / CANVAS_WIDTH) * 100}%`,
              minHeight: `${(node.h / CANVAS_HEIGHT) * 100}%`,
            } as CSSProperties;
            return (
              <button
                key={node.id}
                type="button"
                className={`project-workflow-node is-${node.tone}${activeId === node.id ? " is-active" : ""}`}
                style={style}
                onClick={() => setActiveId(node.id)}
                aria-pressed={activeId === node.id}
              >
                <span aria-hidden="true">{getToneLabel(node.tone)}</span>
                <strong>{node.title}</strong>
              </button>
            );
          })}

          {activeNode ? (
            <aside className={`project-node-popover is-${activeNode.tone}`} style={popupStyle} aria-live="polite">
              <button
                type="button"
                className="project-node-popover-close"
                onClick={() => setActiveId(null)}
                aria-label="Close workflow explanation"
              >
                X
              </button>
              <span>{activeNode.eyebrow}</span>
              <h3>{activeNode.title}</h3>
              <p>{activeNode.text}</p>
              <div>
                {activeNode.tags.map((item) => (
                  <em key={item}>{item}</em>
                ))}
              </div>
            </aside>
          ) : null}
        </div>
      </div>
    </section>
  );
}

function buildEdgePath(from: WorkflowNode, to: WorkflowNode, edge: WorkflowEdge) {
  const start = getAnchor(from, edge.fromSide);
  const end = getAnchor(to, edge.toSide);
  const c1 = getControlPoint(start, end, edge.fromSide);
  const c2 = getControlPoint(end, start, edge.toSide);
  return `M ${start.x} ${start.y} C ${c1.x} ${c1.y}, ${c2.x} ${c2.y}, ${end.x} ${end.y}`;
}

function getAnchor(node: WorkflowNode, side: AnchorSide) {
  if (side === "left") return { x: node.x, y: node.y + node.h / 2 };
  if (side === "right") return { x: node.x + node.w, y: node.y + node.h / 2 };
  if (side === "top") return { x: node.x + node.w / 2, y: node.y };
  return { x: node.x + node.w / 2, y: node.y + node.h };
}

function getControlPoint(start: { x: number; y: number }, end: { x: number; y: number }, side: AnchorSide) {
  const horizontal = Math.max(52, Math.abs(end.x - start.x) * 0.5);
  const vertical = Math.max(52, Math.abs(end.y - start.y) * 0.48);
  if (side === "left") return { x: start.x - horizontal, y: start.y };
  if (side === "right") return { x: start.x + horizontal, y: start.y };
  if (side === "top") return { x: start.x, y: start.y - vertical };
  return { x: start.x, y: start.y + vertical };
}

function getPopupStyle(node: WorkflowNode): CSSProperties {
  const popupWidth = 292;
  const popupHeight = 188;
  const preferredX = node.x > 1040 ? node.x - popupWidth - 18 : node.x + node.w + 18;
  const preferredY = node.y > 420 ? node.y - popupHeight + node.h : node.y - 10;

  return {
    left: `${(clamp(preferredX, 18, CANVAS_WIDTH - popupWidth - 18) / CANVAS_WIDTH) * 100}%`,
    top: `${(clamp(preferredY, 18, CANVAS_HEIGHT - popupHeight - 18) / CANVAS_HEIGHT) * 100}%`,
  };
}

function clamp(value: number, min: number, max: number) {
  return Math.min(max, Math.max(min, value));
}

function getToneLabel(tone: WorkflowTone): string {
  if (tone === "source") return "SRC";
  if (tone === "prep") return "PREP";
  if (tone === "eda") return "EDA";
  if (tone === "hypothesis") return "TEST";
  if (tone === "ml") return "ML";
  return "OUT";
}
