import { useEffect, useRef } from "react";
import Plotly from "plotly.js-dist-min";
import type { Config, Data, Layout } from "plotly.js-dist-min";

import type { TelemetryFigureModel } from "./telemetryFigureModel";

export interface ZoomCommand {
  id: number;
  mode: "first" | "last" | "reset";
}

interface PlotlyTelemetryFigureProps {
  model: TelemetryFigureModel;
  zoomCommand?: ZoomCommand | null;
  onDistanceSelect?: (distanceM: number) => void;
}

interface PlotlyPointEvent {
  points?: Array<{ x?: number | string }>;
}

interface PlotlyEventElement extends HTMLDivElement {
  on?: (event: string, handler: (event: PlotlyPointEvent) => void) => void;
  removeListener?: (event: string, handler: (event: PlotlyPointEvent) => void) => void;
}

function yAxisReference(index: number): string {
  return index === 0 ? "y" : `y${index + 1}`;
}

function yAxisLayoutKey(index: number): string {
  return index === 0 ? "yaxis" : `yaxis${index + 1}`;
}

function panelDomains(panelCount: number): Array<[number, number]> {
  const gap = panelCount > 1 ? 0.035 : 0;
  const usable = 1 - gap * Math.max(panelCount - 1, 0);
  const height = usable / panelCount;

  return Array.from({ length: panelCount }, (_, index) => {
    const top = 1 - index * (height + gap);
    const bottom = top - height;
    return [Math.max(0, bottom), Math.min(1, top)];
  });
}

export function PlotlyTelemetryFigure({
  model,
  zoomCommand,
  onDistanceSelect,
}: PlotlyTelemetryFigureProps) {
  const containerRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    const container = containerRef.current;
    if (container === null) {
      return;
    }

    const traces: Data[] = [];
    const domains = panelDomains(model.panels.length);
    const layout: Partial<Layout> & Record<string, unknown> = {
      autosize: true,
      height: Math.max(380, 158 * model.panels.length + 90),
      hovermode: "x unified",
      dragmode: "zoom",
      uirevision: "ome-analysis-view",
      font: { color: "#a9b8cf", family: "Inter, system-ui, sans-serif", size: 11 },
      margin: { l: 106, r: 30, t: 64, b: 52 },
      showlegend: true,
      legend: {
        orientation: "h",
        x: 0,
        y: 1.04,
        font: { size: 11, color: "#cdd8e7" },
      },
      xaxis: {
        title: { text: `Distance (${model.distanceUnit})` },
        fixedrange: false,
        showgrid: true,
        gridcolor: "#273448",
        zeroline: false,
        color: "#a9b8cf",
        showspikes: true,
        spikemode: "across",
        spikesnap: "cursor",
        spikecolor: "#a9b8cf",
      },
      paper_bgcolor: "rgba(0,0,0,0)",
      plot_bgcolor: "rgba(0,0,0,0)",
    };

    model.panels.forEach((panel, panelIndex) => {
      const yaxis = yAxisReference(panelIndex);
      const layoutKey = yAxisLayoutKey(panelIndex);
      layout[layoutKey] = {
        domain: domains[panelIndex],
        title: { text: `${panel.concept} (${panel.unit})`, font: { size: 11 } },
        fixedrange: false,
        showgrid: true,
        gridcolor: "#273448",
        zeroline: panel.kind === "delta",
        zerolinecolor: "#65778f",
        color: "#a9b8cf",
      };

      panel.traces.forEach((trace) => {
        const color = panel.kind === "delta"
          ? "#5fd3ef"
          : trace.name === "Lap A"
            ? "#5dd6c0"
            : "#f6ad72";
        traces.push({
          type: "scatter",
          mode: "lines",
          x: panel.distanceM as number[],
          y: trace.values as number[],
          name: panel.kind === "delta"
            ? trace.name
            : `${panel.concept} · ${trace.name}`,
          xaxis: "x",
          yaxis,
          line: {
            color,
            width: panel.kind === "delta" ? 2.6 : 1.8,
            dash: trace.lineDash,
            shape: trace.stepShape,
          },
          hovertemplate: panel.kind === "delta"
            ? `%{x:.2f} ${model.distanceUnit}<br>B - A: %{y:.4f} ${panel.unit}<extra></extra>`
            : `%{x:.2f} ${model.distanceUnit}<br>%{y} ${panel.unit}<extra>%{fullData.name}</extra>`,
        });
      });
    });

    const config: Partial<Config> = {
      responsive: true,
      displaylogo: false,
      scrollZoom: true,
      displayModeBar: true,
      modeBarButtonsToRemove: ["lasso2d", "select2d"],
      toImageButtonOptions: {
        format: "png",
        filename: "ome-telemetry-comparison",
        scale: 2,
      },
    };

    void Plotly.react(container, traces, layout, config);

    return () => {
      Plotly.purge(container);
    };
  }, [model]);

  useEffect(() => {
    const plot = containerRef.current as PlotlyEventElement | null;
    if (plot === null || onDistanceSelect === undefined) {
      return;
    }

    const handlePoint = (event: PlotlyPointEvent) => {
      const x = event.points?.[0]?.x;
      if (typeof x === "number" && Number.isFinite(x)) {
        onDistanceSelect(x);
      }
    };

    plot.on?.("plotly_click", handlePoint);
    return () => {
      plot.removeListener?.("plotly_click", handlePoint);
    };
  }, [onDistanceSelect]);

  useEffect(() => {
    const container = containerRef.current;
    const distances = model.panels[0]?.distanceM;
    if (container === null || zoomCommand == null || distances === undefined) {
      return;
    }
    const first = distances[0];
    const last = distances.at(-1);
    if (first === undefined || last === undefined) {
      return;
    }

    if (zoomCommand.mode === "reset") {
      void Plotly.relayout(container, { "xaxis.autorange": true } as Partial<Layout>);
      return;
    }

    const midpoint = (first + last) / 2;
    const range = zoomCommand.mode === "first"
      ? [first, midpoint]
      : [midpoint, last];
    void Plotly.relayout(container, { "xaxis.range": range } as Partial<Layout>);
  }, [zoomCommand, model]);

  return (
    <div
      ref={containerRef}
      className="telemetry-plot"
      role="img"
      aria-label="Synchronized telemetry plots"
    />
  );
}
