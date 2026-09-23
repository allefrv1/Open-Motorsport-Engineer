import { describe, expect, it } from "vitest";

import type { ComparisonReport } from "../src/api";
import { buildTelemetryFigureModel } from "../src/telemetryFigureModel";

const distance = [0, 25, 50, 75, 100];
const delta = [0, 0.02, 0.08, 0.14, 0.2];
const speedA = [40, 42, 44, 43, 45];
const speedB = [39, 43, 45, 44, 46];
const steeringA = [0, 0.1, 0.2, 0.1, 0];
const steeringB = [0, 0.12, 0.22, 0.08, 0];
const engineA = [500, 510, 520, 530, 540];
const engineB = [505, 515, 525, 535, 545];

interface ExpectedTrace {
  name: string;
  values: readonly number[];
  lineDash: string;
  stepShape?: string;
}

interface ExpectedPanel {
  concept: string;
  kind: string;
  unit: string;
  distanceM: readonly number[];
  traces: readonly ExpectedTrace[];
}

interface ExpectedFigureModel {
  distanceUnit: string;
  panels: readonly ExpectedPanel[];
}

const report = {
  comparison: {
    distance_grid_m: distance,
    delta_b_vs_a_s: delta,
  },
  continuous_overlays: [
    {
      canonical_concept: "engine.speed",
      unit: "rad/s",
      distance_grid_m: distance,
      lap_a_values: engineA,
      lap_b_values: engineB,
    },
    {
      canonical_concept: "vehicle.speed",
      unit: "m/s",
      distance_grid_m: distance,
      lap_a_values: speedA,
      lap_b_values: speedB,
    },
    {
      canonical_concept: "driver.steering",
      unit: "rad",
      distance_grid_m: distance,
      lap_a_values: steeringA,
      lap_b_values: steeringB,
    },
  ],
  gear_overlay: {
    canonical_concept: "transmission.gear",
    unit: "gear",
    distance_grid_m: distance,
    lap_a_gears: [2, 3, 3, 4, 4],
    lap_b_gears: [2, 2, 3, 4, 4],
  },
} as unknown as ComparisonReport;

describe("telemetry investigation figure model", () => {
  it("keeps delta first and orders available overlays by the accepted concept order", () => {
    const model = buildTelemetryFigureModel(report) as ExpectedFigureModel;

    expect(model.panels.map((panel) => panel.concept)).toEqual([
      "delta_b_vs_a",
      "vehicle.speed",
      "driver.steering",
      "engine.speed",
      "transmission.gear",
    ]);
  });

  it("passes server arrays through without numerical modification", () => {
    const model = buildTelemetryFigureModel(report) as ExpectedFigureModel;

    const deltaPanel = model.panels[0];
    const speedPanel = model.panels[1];

    expect(deltaPanel.distanceM).toBe(distance);
    expect(deltaPanel.traces[0].values).toBe(delta);

    expect(speedPanel.distanceM).toBe(distance);
    expect(speedPanel.traces[0].values).toBe(speedA);
    expect(speedPanel.traces[1].values).toBe(speedB);
  });

  it("uses redundant Lap A and Lap B line styles", () => {
    const model = buildTelemetryFigureModel(report) as ExpectedFigureModel;
    const speedPanel = model.panels[1];

    expect(speedPanel.traces.map((trace) => [trace.name, trace.lineDash])).toEqual([
      ["Lap A", "solid"],
      ["Lap B", "dash"],
    ]);
  });

  it("marks gear as discrete step presentation instead of continuous interpolation", () => {
    const model = buildTelemetryFigureModel(report) as ExpectedFigureModel;
    const gearPanel = model.panels.at(-1);

    expect(gearPanel?.concept).toBe("transmission.gear");
    expect(gearPanel?.kind).toBe("discrete");
    expect(gearPanel?.traces.every((trace) => trace.stepShape === "hv")).toBe(true);
  });

  it("does not synthesize missing overlays", () => {
    const model = buildTelemetryFigureModel(report) as ExpectedFigureModel;
    const concepts = model.panels.map((panel) => panel.concept);

    expect(concepts).not.toContain("driver.throttle");
    expect(concepts).not.toContain("driver.brake");
  });

  it("keeps the accepted distance basis on every panel", () => {
    const model = buildTelemetryFigureModel(report) as ExpectedFigureModel;

    expect(model.distanceUnit).toBe("m");
    expect(model.panels.every((panel) => panel.distanceM === distance)).toBe(true);
  });

  it("keeps units adjacent to every plotted channel identity", () => {
    const model = buildTelemetryFigureModel(report) as ExpectedFigureModel;

    expect(
      model.panels.map((panel) => [panel.concept, panel.unit]),
    ).toEqual([
      ["delta_b_vs_a", "s"],
      ["vehicle.speed", "m/s"],
      ["driver.steering", "rad"],
      ["engine.speed", "rad/s"],
      ["transmission.gear", "gear"],
    ]);
  });
});
