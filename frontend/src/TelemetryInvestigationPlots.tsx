import { useCallback, useEffect, useMemo, useState } from "react";

import type { ComparisonReport } from "./api";
import { PlotlyTelemetryFigure, type ZoomCommand } from "./PlotlyTelemetryFigure";
import {
  buildTelemetryFigureModel,
  type TelemetryFigurePanel,
} from "./telemetryFigureModel";

interface TelemetryInvestigationPlotsProps {
  report: ComparisonReport;
}

function exactValuesLabel(panel: TelemetryFigurePanel): string {
  return panel.kind === "delta"
    ? "Delta B - A exact values"
    : `${panel.concept} exact values`;
}

function valueHeading(panel: TelemetryFigurePanel, traceName: string): string {
  if (panel.kind === "delta") {
    return `B - A (${panel.unit})`;
  }
  return `${traceName} (${panel.unit})`;
}

function ExactValuesTable({ panel }: { panel: TelemetryFigurePanel }) {
  const label = exactValuesLabel(panel);

  return (
    <details className="exact-values">
      <summary>{label}</summary>
      <div className="table-scroll">
        <table aria-label={label}>
          <thead>
            <tr>
              <th scope="col">Distance (m)</th>
              {panel.traces.map((trace) => (
                <th scope="col" key={trace.name}>
                  {valueHeading(panel, trace.name)}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {panel.distanceM.map((distanceM, index) => (
              <tr key={`${panel.concept}-${distanceM}-${index}`}>
                <td>{String(distanceM)}</td>
                {panel.traces.map((trace) => (
                  <td key={trace.name}>{String(trace.values[index])}</td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </details>
  );
}

export function TelemetryInvestigationPlots({
  report,
}: TelemetryInvestigationPlotsProps) {
  const model = useMemo(() => buildTelemetryFigureModel(report), [report]);
  const [visibleChannels, setVisibleChannels] = useState<string[]>(
    () => model.panels.filter((panel) => panel.kind !== "delta").map((panel) => panel.concept),
  );
  const [cursorIndex, setCursorIndex] = useState(0);
  const [zoomCommand, setZoomCommand] = useState<ZoomCommand | null>(null);

  useEffect(() => {
    setVisibleChannels(
      model.panels.filter((panel) => panel.kind !== "delta").map((panel) => panel.concept),
    );
    setCursorIndex(0);
    setZoomCommand(null);
  }, [model]);

  const visibleModel = useMemo(
    () => ({
      ...model,
      panels: model.panels.filter(
        (panel) => panel.kind === "delta" || visibleChannels.includes(panel.concept),
      ),
    }),
    [model, visibleChannels],
  );

  const distanceGrid = model.panels[0]?.distanceM ?? [];
  const maximumIndex = Math.max(0, distanceGrid.length - 1);
  const safeIndex = Math.min(cursorIndex, maximumIndex);
  const selectedDistance = distanceGrid[safeIndex];

  const selectPlotDistance = useCallback(
    (distance: number) => {
      const exactIndex = distanceGrid.indexOf(distance);
      if (exactIndex >= 0) {
        setCursorIndex(exactIndex);
      }
    },
    [distanceGrid],
  );

  function toggleChannel(concept: string) {
    setVisibleChannels((current) =>
      current.includes(concept)
        ? current.filter((item) => item !== concept)
        : [...current, concept],
    );
  }

  function zoom(mode: ZoomCommand["mode"]) {
    setZoomCommand((previous) => ({ id: (previous?.id ?? 0) + 1, mode }));
  }

  return (
    <section
      className="telemetry-investigation"
      aria-labelledby="telemetry-investigation-heading"
    >
      <div className="section-heading">
        <div>
          <p className="eyebrow">Measured and derived evidence</p>
          <h2 id="telemetry-investigation-heading">Synchronized telemetry</h2>
        </div>
        <p>
          Shared distance axis · Lap A solid · Lap B dashed. Zoom or pan the plot;
          source values are never interpolated in the browser.
        </p>
      </div>

      <div className="plot-workspace">
        <div className="plot-toolbar" aria-label="Plot controls">
          <div className="plot-toolbar__group" role="group" aria-label="Distance zoom">
            <button type="button" onClick={() => zoom("first")}>Focus first half</button>
            <button type="button" onClick={() => zoom("last")}>Focus second half</button>
            <button type="button" onClick={() => zoom("reset")}>Reset zoom</button>
          </div>
          <span className="plot-toolbar__hint">Scroll to zoom · Drag to select · Click to inspect</span>
        </div>

        <div className="channel-picker" role="group" aria-label="Visible telemetry channels">
          <span className="channel-picker__baseline">Derived · B - A</span>
          {model.panels.filter((panel) => panel.kind !== "delta").map((panel) => (
            <label className="channel-toggle" key={panel.concept}>
              <input
                type="checkbox"
                checked={visibleChannels.includes(panel.concept)}
                onChange={() => toggleChannel(panel.concept)}
                aria-label={`${panel.concept} (${panel.unit})`}
              />
              <span>Measured · {panel.concept}</span>
              <small>{panel.unit}</small>
            </label>
          ))}
        </div>

        <div className="telemetry-plot-scroll">
          <PlotlyTelemetryFigure
            model={visibleModel}
            zoomCommand={zoomCommand}
            onDistanceSelect={selectPlotDistance}
          />
        </div>

        <section className="inspector" role="region" aria-label="Inspection cursor">
          <div className="inspector__top">
            <div>
              <p className="eyebrow">Exact source-grid inspection</p>
              <h3>Inspection cursor</h3>
            </div>
            <output className="inspector__distance">{selectedDistance ?? "—"} m</output>
          </div>
          <label htmlFor="telemetry-cursor">Inspection distance point</label>
          <input
            id="telemetry-cursor"
            type="range"
            min={0}
            max={maximumIndex}
            step={1}
            value={safeIndex}
            onChange={(event) => setCursorIndex(Number(event.currentTarget.value))}
            disabled={distanceGrid.length === 0}
          />
          <p className="inspector__help">
            Use arrow keys to move between returned distance samples, or click a plotted point.
            No values are estimated between samples.
          </p>
          <div className="inspector__readouts">
            {visibleModel.panels.map((panel) => {
              const index = selectedDistance === undefined
                ? -1
                : panel.distanceM.indexOf(selectedDistance);
              return (
                <div className="inspector__readout" key={panel.concept}>
                  <span>{panel.kind === "delta" ? "Delta readout" : `Readout · ${panel.concept}`}</span>
                  <div className="inspector__values">
                    {panel.traces.map((trace) => (
                      <div key={trace.name}>
                        <small>{trace.name}</small>
                        <strong>
                          {index >= 0 && trace.values[index] !== undefined
                            ? `${trace.values[index]} ${panel.unit}`
                            : "No aligned point"}
                        </strong>
                      </div>
                    ))}
                  </div>
                </div>
              );
            })}
          </div>
        </section>
      </div>

      <div className="raw-data-disclosure">
        <h3>Exact data tables</h3>
        <div className="exact-values-list">
          {model.panels.map((panel) => (
            <ExactValuesTable panel={panel} key={panel.concept} />
          ))}
        </div>
      </div>
    </section>
  );
}
