import type { ComparisonReport } from "./api";
import { PlotlyTelemetryFigure } from "./PlotlyTelemetryFigure";
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

function valueHeading(
  panel: TelemetryFigurePanel,
  traceName: string,
): string {
  if (panel.kind === "delta") {
    return `B - A (${panel.unit})`;
  }
  return `${traceName} (${panel.unit})`;
}

function ExactValuesTable({
  panel,
}: {
  panel: TelemetryFigurePanel;
}) {
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
  const model = buildTelemetryFigureModel(report);

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
          All panels use the server comparison distance basis. Lap A is solid;
          Lap B is dashed. The browser does not interpolate or smooth telemetry.
        </p>
      </div>

      <PlotlyTelemetryFigure model={model} />

      <div className="exact-values-list">
        {model.panels.map((panel) => (
          <ExactValuesTable panel={panel} key={panel.concept} />
        ))}
      </div>
    </section>
  );
}
