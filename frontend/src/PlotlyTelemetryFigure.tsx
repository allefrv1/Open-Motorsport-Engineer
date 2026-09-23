import { useEffect, useRef } from "react";
import Plotly from "plotly.js-dist-min";
import type { Config, Data, Layout } from "plotly.js-dist-min";

import type { TelemetryFigureModel } from "./telemetryFigureModel";

interface PlotlyTelemetryFigureProps {
  model: TelemetryFigureModel;
}

function yAxisReference(index: number): string {
  return index === 0 ? "y" : `y${index + 1}`;
}

function yAxisLayoutKey(index: number): string {
  return index === 0 ? "yaxis" : `yaxis${index + 1}`;
}

function panelDomains(panelCount: number): Array<[number, number]> {
  const gap = panelCount > 1 ? 0.025 : 0;
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
      hovermode: "x unified",
      margin: { l: 72, r: 24, t: 20, b: 58 },
      showlegend: true,
      legend: {
        orientation: "h",
        x: 0,
        y: 1.04,
      },
      xaxis: {
        title: { text: `Distance (${model.distanceUnit})` },
        fixedrange: false,
        showgrid: true,
        zeroline: false,
      },
      paper_bgcolor: "rgba(0,0,0,0)",
      plot_bgcolor: "rgba(0,0,0,0)",
    };

    model.panels.forEach((panel, panelIndex) => {
      const yaxis = yAxisReference(panelIndex);
      const layoutKey = yAxisLayoutKey(panelIndex);
      layout[layoutKey] = {
        domain: domains[panelIndex],
        title: { text: `${panel.concept} (${panel.unit})` },
        fixedrange: false,
        showgrid: true,
        zeroline: panel.kind === "delta",
      };

      panel.traces.forEach((trace) => {
        traces.push({
          type: "scatter",
          mode: "lines",
          x: panel.distanceM as Data["x"],
          y: trace.values as Data["y"],
          name:
            panel.kind === "delta"
              ? trace.name
              : `${panel.concept} · ${trace.name}`,
          xaxis: "x",
          yaxis,
          line: {
            dash: trace.lineDash,
            shape: trace.stepShape,
          },
          hovertemplate:
            panel.kind === "delta"
              ? `%{x:.2f} ${model.distanceUnit}<br>B - A: %{y:.4f} ${panel.unit}<extra></extra>`
              : `%{x:.2f} ${model.distanceUnit}<br>%{y} ${panel.unit}<extra>%{fullData.name}</extra>`,
        });
      });
    });

    const config: Partial<Config> = {
      responsive: true,
      displaylogo: false,
      scrollZoom: true,
    };

    void Plotly.react(container, traces, layout, config);

    return () => {
      Plotly.purge(container);
    };
  }, [model]);

  return (
    <div
      ref={containerRef}
      className="telemetry-plot"
      role="img"
      aria-label="Synchronized telemetry plots"
    />
  );
}
