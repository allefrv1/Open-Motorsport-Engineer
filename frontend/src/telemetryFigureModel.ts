import type {
  ComparisonReport,
  ContinuousOverlay,
  GearOverlay,
} from "./api";

export type FigurePanelKind = "delta" | "continuous" | "discrete";
export type FigureLineDash = "solid" | "dash";

export interface TelemetryFigureTrace {
  name: string;
  values: readonly number[];
  lineDash: FigureLineDash;
  stepShape?: "hv";
}

export interface TelemetryFigurePanel {
  concept: string;
  kind: FigurePanelKind;
  unit: string;
  distanceM: readonly number[];
  traces: readonly TelemetryFigureTrace[];
}

export interface TelemetryFigureModel {
  distanceUnit: "m";
  panels: readonly TelemetryFigurePanel[];
}

const CONTINUOUS_CONCEPT_ORDER = [
  "vehicle.speed",
  "driver.throttle",
  "driver.brake",
  "driver.steering",
  "engine.speed",
] as const;

function continuousPanel(
  overlay: ContinuousOverlay,
): TelemetryFigurePanel {
  return {
    concept: overlay.canonical_concept,
    kind: "continuous",
    unit: overlay.unit,
    distanceM: overlay.distance_grid_m,
    traces: [
      {
        name: "Lap A",
        values: overlay.lap_a_values,
        lineDash: "solid",
      },
      {
        name: "Lap B",
        values: overlay.lap_b_values,
        lineDash: "dash",
      },
    ],
  };
}

function gearPanel(overlay: GearOverlay): TelemetryFigurePanel {
  return {
    concept: overlay.canonical_concept,
    kind: "discrete",
    unit: overlay.unit,
    distanceM: overlay.distance_grid_m,
    traces: [
      {
        name: "Lap A",
        values: overlay.lap_a_gears,
        lineDash: "solid",
        stepShape: "hv",
      },
      {
        name: "Lap B",
        values: overlay.lap_b_gears,
        lineDash: "dash",
        stepShape: "hv",
      },
    ],
  };
}

export function buildTelemetryFigureModel(
  report: ComparisonReport,
): TelemetryFigureModel {
  const overlayByConcept = new Map(
    report.continuous_overlays.map((overlay) => [
      overlay.canonical_concept,
      overlay,
    ]),
  );

  const panels: TelemetryFigurePanel[] = [
    {
      concept: "delta_b_vs_a",
      kind: "delta",
      unit: report.comparison.time_unit,
      distanceM: report.comparison.distance_grid_m,
      traces: [
        {
          name: "B - A",
          values: report.comparison.delta_b_vs_a_s,
          lineDash: "solid",
        },
      ],
    },
  ];

  for (const concept of CONTINUOUS_CONCEPT_ORDER) {
    const overlay = overlayByConcept.get(concept);
    if (overlay !== undefined) {
      panels.push(continuousPanel(overlay));
    }
  }

  if (report.gear_overlay !== null) {
    panels.push(gearPanel(report.gear_overlay));
  }

  return {
    distanceUnit: "m",
    panels,
  };
}
