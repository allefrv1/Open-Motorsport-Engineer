import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import Plotly from "plotly.js-dist-min";
import { afterEach, describe, expect, it, vi } from "vitest";

import type { ComparisonReport } from "../src/api";
import { TelemetryInvestigationPlots } from "../src/TelemetryInvestigationPlots";

vi.mock("plotly.js-dist-min", () => ({
  default: {
    react: vi.fn().mockResolvedValue(undefined),
    purge: vi.fn(),
  },
}));

const distance = [0, 25, 50, 75, 100];

const report = {
  comparison: {
    time_unit: "s",
    distance_grid_m: distance,
    delta_b_vs_a_s: [0, 0.02, 0.08, 0.14, 0.2],
  },
  continuous_overlays: [
    {
      canonical_concept: "vehicle.speed",
      unit: "m/s",
      distance_grid_m: distance,
      lap_a_values: [40, 42, 44, 43, 45],
      lap_b_values: [39, 43, 45, 44, 46],
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

afterEach(() => {
  cleanup();
  vi.clearAllMocks();
});

describe("synchronized telemetry investigation plots", () => {
  it("renders one synchronized Plotly figure from the server-returned arrays", async () => {
    render(<TelemetryInvestigationPlots report={report} />);

    await waitFor(() => expect(vi.mocked(Plotly.react)).toHaveBeenCalledTimes(1));

    const [, traces, layout, config] = vi.mocked(Plotly.react).mock.calls[0] as [
      HTMLElement,
      Array<Record<string, unknown>>,
      Record<string, unknown>,
      Record<string, unknown>,
    ];

    expect(traces).toHaveLength(5);
    expect(traces.map((trace) => trace.name)).toEqual([
      "B - A",
      "vehicle.speed · Lap A",
      "vehicle.speed · Lap B",
      "transmission.gear · Lap A",
      "transmission.gear · Lap B",
    ]);
    expect(traces.every((trace) => trace.x === distance)).toBe(true);
    expect(layout.hovermode).toBe("x unified");
    expect(config.responsive).toBe(true);
  });

  it("uses redundant line styles and discrete step shape for gear", async () => {
    render(<TelemetryInvestigationPlots report={report} />);

    await waitFor(() => expect(vi.mocked(Plotly.react)).toHaveBeenCalledTimes(1));
    const traces = vi.mocked(Plotly.react).mock.calls[0][1] as Array<{
      name: string;
      line?: { dash?: string; shape?: string };
    }>;

    expect(traces.find((trace) => trace.name === "vehicle.speed · Lap A")?.line?.dash).toBe(
      "solid",
    );
    expect(traces.find((trace) => trace.name === "vehicle.speed · Lap B")?.line?.dash).toBe(
      "dash",
    );
    expect(
      traces.find((trace) => trace.name === "transmission.gear · Lap A")?.line?.shape,
    ).toBe("hv");
    expect(
      traces.find((trace) => trace.name === "transmission.gear · Lap B")?.line?.shape,
    ).toBe("hv");
  });

  it("exposes exact server values through semantic tables", () => {
    render(<TelemetryInvestigationPlots report={report} />);

    fireEvent.click(screen.getByText("vehicle.speed exact values"));
    const speedTable = screen.getByRole("table", {
      name: "vehicle.speed exact values",
    });

    expect(speedTable.textContent).toContain("Distance (m)");
    expect(speedTable.textContent).toContain("Lap A (m/s)");
    expect(speedTable.textContent).toContain("Lap B (m/s)");
    expect(speedTable.textContent).toContain("25");
    expect(speedTable.textContent).toContain("42");
    expect(speedTable.textContent).toContain("43");

    fireEvent.click(screen.getByText("Delta B - A exact values"));
    const deltaTable = screen.getByRole("table", {
      name: "Delta B - A exact values",
    });
    expect(deltaTable.textContent).toContain("0.2");
  });

  it("does not synthesize a missing throttle panel or exact-value table", () => {
    render(<TelemetryInvestigationPlots report={report} />);

    expect(screen.queryByText("driver.throttle exact values")).toBeNull();
  });

  it("purges the Plotly figure when the visualization unmounts", async () => {
    const view = render(<TelemetryInvestigationPlots report={report} />);

    await waitFor(() => expect(vi.mocked(Plotly.react)).toHaveBeenCalledTimes(1));
    view.unmount();

    expect(vi.mocked(Plotly.purge)).toHaveBeenCalledTimes(1);
  });
});
