"use client";

import { AnimatePresence, motion } from "framer-motion";
import { useState } from "react";
import type { EdaPlot } from "@/types";

const filters = [
  { id: "all", label: "All plots" },
  { id: "combined", label: "Combined" },
  { id: "youtube", label: "YouTube" },
  { id: "spotify", label: "Spotify" },
  { id: "prime-netflix", label: "Netflix + Prime" },
];

const groupLabels: Record<string, string> = {
  combined: "Combined cross-platform plots",
  youtube: "YouTube plots",
  spotify: "Spotify plots",
  "prime-netflix": "Netflix + Prime Video plots",
};

type EdaGalleryProps = {
  plots: EdaPlot[];
  curatedOnly?: boolean;
};

export function EdaGallery({ plots, curatedOnly = false }: EdaGalleryProps) {
  const [activeFilter, setActiveFilter] = useState("all");
  const [selectedPlot, setSelectedPlot] = useState<EdaPlot | null>(null);
  const visiblePlots = plots.filter((plot) => {
    const passesCurated = curatedOnly ? plot.curated : true;
    const passesFilter = activeFilter === "all" || plot.group === activeFilter;
    return passesCurated && passesFilter;
  });
  const visibleGroups = Array.from(new Set(visiblePlots.map((plot) => plot.group)));

  return (
    <div className="gallery-shell">
      {!curatedOnly ? (
        <div className="gallery-filters" aria-label="EDA plot filters">
          {filters.map((filter) => (
            <button
              key={filter.id}
              className={activeFilter === filter.id ? "is-active" : ""}
              type="button"
              onClick={() => setActiveFilter(filter.id)}
            >
              {filter.label}
            </button>
          ))}
        </div>
      ) : null}

      <div className="gallery-group-stack">
        {visibleGroups.map((groupId) => {
          const groupPlots = visiblePlots.filter((plot) => plot.group === groupId);
          return (
            <details className="gallery-group" key={groupId} open>
              <summary>
                <span>{groupLabels[groupId] ?? groupId}</span>
                <small>{groupPlots.length} plots</small>
              </summary>
              <div className="plot-grid">
                {groupPlots.map((plot, index) => {
                  const title = plot.title || plot.file || "EDA plot";
                  return (
                  <motion.button
                    key={plot.id}
                    className="plot-card"
                    type="button"
                    onClick={() => setSelectedPlot(plot)}
                    initial={{ opacity: 0, y: 18 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    transition={{ delay: Math.min(index * 0.035, 0.35) }}
                  >
                    <span className="plot-card-top">
                      <span className="plot-badge">{plot.platform}</span>
                      <span className="plot-zoom-icon" aria-hidden="true">
                        Open
                      </span>
                    </span>
                    <img src={plot.src} alt={title} loading="lazy" />
                    <span className="plot-title">{title}</span>
                    <span className="plot-caption">{plot.caption}</span>
                  </motion.button>
                  );
                })}
              </div>
            </details>
          );
        })}
      </div>

      <AnimatePresence>
        {selectedPlot ? (
          <motion.div
            className="modal-backdrop"
            role="dialog"
            aria-modal="true"
            aria-label={selectedPlot.title}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => setSelectedPlot(null)}
          >
            <motion.div
              className="modal-panel"
              initial={{ opacity: 0, y: 30, scale: 0.96 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, y: 20, scale: 0.96 }}
              onClick={(event) => event.stopPropagation()}
            >
              <div className="modal-header">
                <div>
                  <p className="eyebrow">{selectedPlot.platform}</p>
                  <h2>{selectedPlot.title}</h2>
                  <p>{selectedPlot.caption}</p>
                </div>
                <div className="modal-actions">
                  <a className="modal-close" href={selectedPlot.src} download={selectedPlot.file}>
                    Download
                  </a>
                  <button className="modal-close" type="button" onClick={() => setSelectedPlot(null)}>
                    Close
                  </button>
                </div>
              </div>
              <img src={selectedPlot.src} alt={selectedPlot.title} />
            </motion.div>
          </motion.div>
        ) : null}
      </AnimatePresence>
    </div>
  );
}
