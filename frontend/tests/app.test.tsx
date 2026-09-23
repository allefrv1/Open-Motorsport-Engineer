import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { App } from "../src/App";

type JsonBody = Record<string, unknown>;

function mockResponse(body: JsonBody, status = 200): Response {
  return {
    ok: status >= 200 && status < 300,
    status,
    json: async () => body,
  } as Response;
}

function file(name: string, type: string, content = "fixture"): File {
  return new File([content], name, { type });
}

const successBody = {
  status: "success",
  report: {
    comparison: {
      reference_concept: "lap.distance",
      reference_unit: "m",
      time_concept: "time.elapsed",
      time_unit: "s",
      common_start_m: 0,
      common_end_m: 100,
      distance_grid_m: [0, 25, 50, 75, 100],
      lap_a_elapsed_s: [0, 1, 2, 3, 4],
      lap_b_elapsed_s: [0, 1.02, 2.08, 3.14, 4.2],
      delta_b_vs_a_s: [0, 0.02, 0.08, 0.14, 0.2],
      provenance: {
        algorithm_id: "ome.lap-comparison.distance-linear",
        algorithm_version: "0.1.0",
        parameters: { grid_step_m: 25 },
        reference_concept: "lap.distance",
        reference_unit: "m",
        time_concept: "time.elapsed",
        time_unit: "s",
        common_start_m: 0,
        common_end_m: 100,
        lap_a: {
          context: {
            dataset_fingerprint: "sha256:lap-a",
            session_identifier: "session:a",
            run_identifier: null,
            lap_identifier: "lap:a",
          },
          distance: {
            dataset_fingerprint: "sha256:lap-a",
            source_channel_identifier: "lap_distance_src",
            source_original_name: "Lap Distance",
            canonical_concept: "lap.distance",
            unit: "m",
            transformations: [],
            semantic_id: null,
          },
          elapsed_time: {
            dataset_fingerprint: "sha256:lap-a",
            source_channel_identifier: "time_s",
            source_original_name: "Time",
            canonical_concept: "time.elapsed",
            unit: "s",
            transformations: [],
            semantic_id: null,
          },
        },
        lap_b: {
          context: {
            dataset_fingerprint: "sha256:lap-b",
            session_identifier: "session:b",
            run_identifier: null,
            lap_identifier: "lap:b",
          },
          distance: {
            dataset_fingerprint: "sha256:lap-b",
            source_channel_identifier: "lap_distance_src",
            source_original_name: "Lap Distance",
            canonical_concept: "lap.distance",
            unit: "m",
            transformations: [],
            semantic_id: null,
          },
          elapsed_time: {
            dataset_fingerprint: "sha256:lap-b",
            source_channel_identifier: "time_s",
            source_original_name: "Time",
            canonical_concept: "time.elapsed",
            unit: "s",
            transformations: [],
            semantic_id: null,
          },
        },
      },
    },
    observations: {
      regions: [
        {
          kind: "b_loss",
          start_distance_m: 0,
          end_distance_m: 100,
          start_delta_s: 0,
          end_delta_s: 0.2,
          total_delta_change_s: 0.2,
          interval_count: 4,
        },
      ],
    },
    continuous_overlays: [],
    gear_overlay: null,
    supporting_evidence: [
      {
        canonical_concept: "vehicle.speed",
        kind: "continuous",
        status: "available",
        unit: "m/s",
        issue_codes: [],
        messages: [],
      },
      {
        canonical_concept: "driver.brake",
        kind: "continuous",
        status: "missing",
        unit: null,
        issue_codes: ["missing_evidence"],
        messages: ["Brake evidence is unavailable for Lap B."],
      },
    ],
    provenance: {
      assembler_id: "ome.comparison-report",
      assembler_version: "0.1.0",
      requested_concepts: ["vehicle.speed", "driver.brake"],
    },
  },
};

function selectSources() {
  const lapACsv = file("lap-a.csv", "text/csv");
  const lapASidecar = file("lap-a.ome.json", "application/json");
  const lapBCsv = file("lap-b.csv", "text/csv");
  const lapBSidecar = file("lap-b.ome.json", "application/json");

  fireEvent.change(screen.getByLabelText("Lap A CSV"), {
    target: { files: [lapACsv] },
  });
  fireEvent.change(screen.getByLabelText("Lap A sidecar"), {
    target: { files: [lapASidecar] },
  });
  fireEvent.change(screen.getByLabelText("Lap B CSV"), {
    target: { files: [lapBCsv] },
  });
  fireEvent.change(screen.getByLabelText("Lap B sidecar"), {
    target: { files: [lapBSidecar] },
  });

  return { lapACsv, lapASidecar, lapBCsv, lapBSidecar };
}

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("MVP investigation frontend", () => {
  it("keeps Compare laps disabled until all four source files exist", () => {
    render(<App />);

    const compare = screen.getByRole("button", { name: "Compare laps" });
    expect((compare as HTMLButtonElement).disabled).toBe(true);

    fireEvent.change(screen.getByLabelText("Lap A CSV"), {
      target: { files: [file("lap-a.csv", "text/csv")] },
    });
    fireEvent.change(screen.getByLabelText("Lap A sidecar"), {
      target: { files: [file("lap-a.ome.json", "application/json")] },
    });
    fireEvent.change(screen.getByLabelText("Lap B CSV"), {
      target: { files: [file("lap-b.csv", "text/csv")] },
    });
    expect((compare as HTMLButtonElement).disabled).toBe(true);

    fireEvent.change(screen.getByLabelText("Lap B sidecar"), {
      target: { files: [file("lap-b.ome.json", "application/json")] },
    });
    expect((compare as HTMLButtonElement).disabled).toBe(false);
  });

  it("submits the exact Plan 017 multipart field names", async () => {
    const fetchMock = vi.fn().mockResolvedValue(mockResponse(successBody));
    vi.stubGlobal("fetch", fetchMock);
    render(<App />);

    const selected = selectSources();
    fireEvent.change(screen.getByLabelText("Grid step (m)"), {
      target: { value: "25" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Compare laps" }));

    await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(1));
    const [url, options] = fetchMock.mock.calls[0] as [string, RequestInit];

    expect(url).toBe("/api/v1/ome-csv/comparison-reports");
    expect(options.method).toBe("POST");
    expect(options.body).toBeInstanceOf(FormData);

    const body = options.body as FormData;
    expect(body.get("lap_a_csv")).toBe(selected.lapACsv);
    expect(body.get("lap_a_sidecar")).toBe(selected.lapASidecar);
    expect(body.get("lap_b_csv")).toBe(selected.lapBCsv);
    expect(body.get("lap_b_sidecar")).toBe(selected.lapBSidecar);
    expect(body.get("grid_step_m")).toBe("25");
  });

  it("announces loading and prevents duplicate submission", async () => {
    let resolveFetch: ((response: Response) => void) | undefined;
    const fetchMock = vi.fn().mockImplementation(
      () =>
        new Promise<Response>((resolve) => {
          resolveFetch = resolve;
        }),
    );
    vi.stubGlobal("fetch", fetchMock);
    render(<App />);

    selectSources();
    const compare = screen.getByRole("button", { name: "Compare laps" });
    fireEvent.click(compare);

    expect((await screen.findByRole("status")).textContent).toContain("Comparing laps");
    expect((compare as HTMLButtonElement).disabled).toBe(true);

    fireEvent.click(compare);
    expect(fetchMock).toHaveBeenCalledTimes(1);

    resolveFetch?.(mockResponse(successBody));
    await screen.findByText("+0.200 s");
  });

  it("renders the deterministic success result without recomputing it", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(mockResponse(successBody)));
    render(<App />);

    selectSources();
    fireEvent.change(screen.getByLabelText("Grid step (m)"), {
      target: { value: "25" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Compare laps" }));

    expect(await screen.findByText("+0.200 s")).toBeTruthy();
    expect(screen.getByText("Lap B is slower at the end of the common interval.")).toBeTruthy();
    expect(screen.getByText("Lap A = reference")).toBeTruthy();
    expect(screen.getByText("Delta = Lap B - Lap A")).toBeTruthy();
    expect(screen.getByText("0–100 m")).toBeTruthy();
    expect(screen.getByText("lap-a.csv")).toBeTruthy();
    expect(screen.getByText("lap-b.csv")).toBeTruthy();

    const chart = screen.getByRole("img", { name: "Delta time over distance" });
    expect(chart).toBeTruthy();
    expect(chart.getAttribute("data-point-count")).toBe("5");
  });

  it("renders gain/loss as observations without a causal diagnosis", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(mockResponse(successBody)));
    render(<App />);

    selectSources();
    fireEvent.click(screen.getByRole("button", { name: "Compare laps" }));

    expect(await screen.findByRole("heading", { name: "Observations" })).toBeTruthy();
    expect(screen.getByText("Lap B loss")).toBeTruthy();
    expect(screen.getByText("0–100 m")).toBeTruthy();
    expect(screen.queryByText(/because/i)).toBeNull();
    expect(screen.queryByText(/cause/i)).toBeNull();
  });

  it("keeps Missing Evidence explicit", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(mockResponse(successBody)));
    render(<App />);

    selectSources();
    fireEvent.click(screen.getByRole("button", { name: "Compare laps" }));

    expect(await screen.findByRole("heading", { name: "Supporting evidence" })).toBeTruthy();
    expect(screen.getByText("vehicle.speed")).toBeTruthy();
    expect(screen.getByText("Available")).toBeTruthy();
    expect(screen.getByText("driver.brake")).toBeTruthy();
    expect(screen.getByText("Missing evidence")).toBeTruthy();
    expect(screen.getByText("Brake evidence is unavailable for Lap B.")).toBeTruthy();
  });

  it("makes provenance discoverable through progressive disclosure", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(mockResponse(successBody)));
    render(<App />);

    selectSources();
    fireEvent.click(screen.getByRole("button", { name: "Compare laps" }));
    await screen.findByText("+0.200 s");

    const summary = screen.getByText("Method and provenance");
    expect(summary).toBeTruthy();

    fireEvent.click(summary);
    expect(screen.getByText("ome.lap-comparison.distance-linear")).toBeTruthy();
    expect(screen.getByText("0.1.0")).toBeTruthy();
    expect(screen.getByText("lap_distance_src")).toBeTruthy();
    expect(screen.getByText("time_s")).toBeTruthy();
    expect(screen.getByText("sha256:lap-a")).toBeTruthy();
    expect(screen.getByText("sha256:lap-b")).toBeTruthy();
  });

  it("renders not-ready issues and retains the selected files", async () => {
    const notReady = {
      status: "not_ready",
      stage: "preparation",
      issues: [
        {
          code: "missing_lap_distance",
          message: "Lap B does not provide trustworthy lap distance evidence.",
          lap_side: "b",
          canonical_concept: "lap.distance",
        },
      ],
    };
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(mockResponse(notReady)));
    render(<App />);

    selectSources();
    fireEvent.click(screen.getByRole("button", { name: "Compare laps" }));

    expect(await screen.findByText("Comparison not ready")).toBeTruthy();
    expect(screen.getByText("Preparation")).toBeTruthy();
    expect(
      screen.getByText("Lap B does not provide trustworthy lap distance evidence."),
    ).toBeTruthy();
    expect(screen.getByText("lap.distance")).toBeTruthy();
    expect(screen.getByText("lap-a.csv")).toBeTruthy();
    expect(screen.getByText("lap-b.csv")).toBeTruthy();
  });

  it("shows a recoverable network error and keeps source selection", async () => {
    vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new Error("connection refused")));
    render(<App />);

    selectSources();
    fireEvent.click(screen.getByRole("button", { name: "Compare laps" }));

    expect((await screen.findByRole("alert")).textContent).toContain(
      "Could not reach the local OME API",
    );
    expect(screen.getByText("lap-a.csv")).toBeTruthy();
    expect(screen.getByText("lap-b.csv")).toBeTruthy();
    expect(
      (screen.getByRole("button", { name: "Compare laps" }) as HTMLButtonElement).disabled,
    ).toBe(false);
  });

  it("uses semantic labels for the core source workflow", () => {
    render(<App />);

    expect(screen.getByRole("main")).toBeTruthy();
    expect(screen.getByRole("heading", { name: "Compare two laps" })).toBeTruthy();
    expect(screen.getByLabelText("Lap A CSV").getAttribute("type")).toBe("file");
    expect(screen.getByLabelText("Lap A sidecar").getAttribute("type")).toBe("file");
    expect(screen.getByLabelText("Lap B CSV").getAttribute("type")).toBe("file");
    expect(screen.getByLabelText("Lap B sidecar").getAttribute("type")).toBe("file");
    expect(screen.getByLabelText("Grid step (m)").getAttribute("type")).toBe("number");
  });
});
