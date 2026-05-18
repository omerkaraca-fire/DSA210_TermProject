"use client";

import { AnimatePresence, motion } from "framer-motion";
import { useState } from "react";
import type { EdaPlot } from "@/types";

const galleryGroups = [
  { id: "combined", label: "Combined", title: "Combined cross-platform plots" },
  { id: "youtube", label: "YouTube", title: "YouTube plots" },
  { id: "spotify", label: "Spotify", title: "Spotify plots" },
  { id: "prime-netflix", label: "Netflix + Prime", title: "Netflix + Prime Video plots" },
  { id: "ml-academic", label: "Academic ML", title: "Academic-period ML plots" },
  { id: "ml-summer", label: "Summer ML", title: "Summer-work ML plots" },
  { id: "ml-all", label: "All Classification", title: "All-classification ML plots" },
];

type EdaGalleryProps = {
  plots: EdaPlot[];
  curatedOnly?: boolean;
};

export function EdaGallery({ plots, curatedOnly = false }: EdaGalleryProps) {
  const [selectedPlot, setSelectedPlot] = useState<EdaPlot | null>(null);
  const [selectedByGroup, setSelectedByGroup] = useState<Record<string, string>>({});
  const visiblePlots = plots.filter((plot) => {
    const passesCurated = curatedOnly ? plot.curated : true;
    return passesCurated;
  });
  const configuredGroups = galleryGroups
    .map((group) => ({
      ...group,
      plots: visiblePlots.filter((plot) => plot.group === group.id),
    }))
    .filter((group) => group.plots.length > 0);

  return (
    <div className="gallery-shell">
      <div className="gallery-selector-grid">
        {configuredGroups.map((group, index) => {
          const selectedId = selectedByGroup[group.id] ?? group.plots[0].id;
          const activePlot = group.plots.find((plot) => plot.id === selectedId) ?? group.plots[0];
          const title = activePlot.title || activePlot.file || "EDA plot";
          return (
            <motion.article
              className="gallery-picker-card"
              key={group.id}
              initial={{ opacity: 0, y: 18 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: Math.min(index * 0.04, 0.35) }}
            >
              <div className="gallery-picker-header">
                <div>
                  <p className="plot-badge">{group.label}</p>
                  <h3>{group.title}</h3>
                </div>
                <small>{group.plots.length} plots</small>
              </div>
              <label className="gallery-select-label" htmlFor={`plot-select-${group.id}`}>
                Selected plot
              </label>
              <select
                id={`plot-select-${group.id}`}
                className="gallery-select"
                value={activePlot.id}
                onChange={(event) =>
                  setSelectedByGroup((current) => ({
                    ...current,
                    [group.id]: event.target.value,
                  }))
                }
              >
                {group.plots.map((plot) => (
                  <option key={plot.id} value={plot.id}>
                    {plot.title || plot.file}
                  </option>
                ))}
              </select>
              <button className="plot-card is-selected-plot" type="button" onClick={() => setSelectedPlot(activePlot)}>
                <span className="plot-card-top">
                  <span className="plot-badge">{activePlot.platform}</span>
                  <span className="plot-zoom-icon" aria-hidden="true">
                    Open
                  </span>
                </span>
                <img src={activePlot.src} alt={title} loading="lazy" />
                <span className="plot-title">{title}</span>
                <span className="plot-caption">{activePlot.caption}</span>
              </button>
            </motion.article>
          );
        })}
      </div>

      <div className="gallery-group-stack">
        {visiblePlots
          .filter((plot) => !galleryGroups.some((group) => group.id === plot.group))
          .map((plot, index) => {
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
