import { FormEvent, useMemo, useState } from "react";

import {
  ComparisonReport,
  ComparisonWorkflowResponse,
  SupportingEvidence,
  WorkflowIssue,
  submitComparison,
} from "./api";
import { DeltaChart } from "./DeltaChart";
import { TelemetryInvestigationPlots } from "./TelemetryInvestigationPlots";

interface SourceFileFieldProps {
  id: string;
  label: string;
  accept: string;
  file: File | null;
  onChange: (file: File | null) => void;
}

function SourceFileField({
  id,
  label,
  accept,
  file,
  onChange,
}: SourceFileFieldProps) {
  return (
    <div className="file-field">
      <label htmlFor={id}>{label}</label>
      <input
        id={id}
        type="file"
        accept={accept}
        onChange={(event) => onChange(event.currentTarget.files?.[0] ?? null)}
      />
      <div className="file-name" aria-live="polite">
        {file?.name ?? "No file selected"}
      </div>
    </div>
  );
}

function formatDistance(value: number): string {
  return Number.isInteger(value) ? value.toFixed(0) : value.toFixed(1);
}

function formatDistanceRange(start: number, end: number): string {
  return `${formatDistance(start)}–${formatDistance(end)} m`;
}

function formatSignedSeconds(value: number): string {
  const normalized = Object.is(value, -0) ? 0 : value;
  const sign = normalized >= 0 ? "+" : "";
  return `${sign}${normalized.toFixed(3)} s`;
}

function finalDeltaInterpretation(value: number): string {
  if (value > 0) {
    return "Lap B is slower at the end of the common interval.";
  }
  if (value < 0) {
    return "Lap B is faster at the end of the common interval.";
  }
  return "Lap A and Lap B have equal elapsed time at the end of the common interval.";
}

function observationLabel(kind: string): string {
  if (kind === "b_gain") {
    return "Lap B gain";
  }
  if (kind === "b_loss") {
    return "Lap B loss";
  }
  if (kind === "neutral") {
    return "Neutral";
  }
  return kind;
}

function evidenceStatusLabel(item: SupportingEvidence): string {
  if (item.status === "available") {
    return "Available";
  }
  if (item.status === "missing" || item.status === "missing_evidence") {
    return "Missing evidence";
  }
  if (item.status === "incompatible") {
    return "Incompatible evidence";
  }
  return item.status;
}

function stageLabel(stage: "import" | "preparation" | "report"): string {
  return stage.charAt(0).toUpperCase() + stage.slice(1);
}

function WorkflowIssues({
  stage,
  issues,
}: {
  stage: "import" | "preparation" | "report";
  issues: WorkflowIssue[];
}) {
  return (
    <section
      className="not-ready"
      role="status"
      aria-live="polite"
      aria-labelledby="not-ready-heading"
    >
      <p className="eyebrow">{stageLabel(stage)}</p>
      <h2 id="not-ready-heading">Comparison not ready</h2>
      <ul className="issue-list">
        {issues.map((issue, index) => (
          <li key={`${issue.code}-${index}`}>
            <strong>{issue.message}</strong>
            <div className="issue-meta">
              {issue.lap_side !== null ? (
                <span>Lap {issue.lap_side.toUpperCase()}</span>
              ) : null}
              {issue.canonical_concept !== null ? (
                <code>{issue.canonical_concept}</code>
              ) : null}
            </div>
          </li>
        ))}
      </ul>
    </section>
  );
}

function ComparisonResults({
  report,
}: {
  report: ComparisonReport;
}) {
  const comparison = report.comparison;
  const finalDelta = comparison.delta_b_vs_a_s.at(-1) ?? 0;
  const provenance = comparison.provenance;

  const sourceChannels = Array.from(
    new Set([
      provenance.lap_a.distance.source_channel_identifier,
      provenance.lap_b.distance.source_channel_identifier,
      provenance.lap_a.elapsed_time.source_channel_identifier,
      provenance.lap_b.elapsed_time.source_channel_identifier,
    ]),
  );

  return (
    <section className="results" aria-labelledby="comparison-result-heading">
      <div className="comparison-header">
        <div>
          <p className="eyebrow">Deterministic comparison</p>
          <h2 id="comparison-result-heading">Lap comparison</h2>
          <div className="comparison-meta" aria-label="Comparison method summary">
            <span>Lap A = reference</span>
            <span>Delta = Lap B - Lap A</span>
            <span>
              {formatDistanceRange(
                comparison.common_start_m,
                comparison.common_end_m,
              )}
            </span>
          </div>
        </div>
        <div>
          <p className="delta-value">{formatSignedSeconds(finalDelta)}</p>
          <p className="delta-interpretation">
            {finalDeltaInterpretation(finalDelta)}
          </p>
        </div>
      </div>

      <section className="result-section" aria-labelledby="delta-heading">
        <h2 id="delta-heading">Delta over distance</h2>
        <DeltaChart
          distances={comparison.distance_grid_m}
          deltas={comparison.delta_b_vs_a_s}
        />
      </section>

      <TelemetryInvestigationPlots report={report} />

      <section className="result-section" aria-labelledby="observations-heading">
        <h2 id="observations-heading">Observations</h2>
        {report.observations.regions.length === 0 ? (
          <p>No gain/loss regions were returned by the deterministic observation layer.</p>
        ) : (
          <ul className="observation-list">
            {report.observations.regions.map((region, index) => (
              <li
                className="observation-item"
                key={`${region.kind}-${region.start_distance_m}-${index}`}
              >
                <div className="observation-kind">
                  {observationLabel(region.kind)}
                </div>
                <div className="evidence-detail">
                  <div>
                    Distance{" "}
                    {formatDistanceRange(
                      region.start_distance_m,
                      region.end_distance_m,
                    )}
                  </div>
                  <div>
                    Delta change {formatSignedSeconds(region.total_delta_change_s)}
                  </div>
                </div>
              </li>
            ))}
          </ul>
        )}
      </section>

      <section className="result-section" aria-labelledby="evidence-heading">
        <h2 id="evidence-heading">Supporting evidence</h2>
        <ul className="evidence-list">
          {report.supporting_evidence.map((item) => (
            <li className="evidence-item" key={item.canonical_concept}>
              <div>
                <div className="evidence-concept">{item.canonical_concept}</div>
                <div className="evidence-status">
                  {evidenceStatusLabel(item)}
                </div>
              </div>
              <div className="evidence-detail">
                {item.unit !== null ? <div>Unit: {item.unit}</div> : null}
                {item.messages.map((message) => (
                  <div key={message}>{message}</div>
                ))}
              </div>
            </li>
          ))}
        </ul>
      </section>

      <section className="result-section provenance">
        <details>
          <summary>Method and provenance</summary>
          <dl className="provenance-grid">
            <dt>Algorithm</dt>
            <dd>{provenance.algorithm_id}</dd>

            <dt>Version</dt>
            <dd>{provenance.algorithm_version}</dd>

            <dt>Lap A context</dt>
            <dd>{provenance.lap_a.context.lap_identifier}</dd>

            <dt>Lap B context</dt>
            <dd>{provenance.lap_b.context.lap_identifier}</dd>

            <dt>Lap A dataset</dt>
            <dd>{provenance.lap_a.context.dataset_fingerprint}</dd>

            <dt>Lap B dataset</dt>
            <dd>{provenance.lap_b.context.dataset_fingerprint}</dd>

            <dt>Source channels</dt>
            <dd>
              <ul className="provenance-list">
                {sourceChannels.map((channel) => (
                  <li key={channel}>{channel}</li>
                ))}
              </ul>
            </dd>
          </dl>
        </details>
      </section>
    </section>
  );
}

export function App() {
  const [lapACsv, setLapACsv] = useState<File | null>(null);
  const [lapASidecar, setLapASidecar] = useState<File | null>(null);
  const [lapBCsv, setLapBCsv] = useState<File | null>(null);
  const [lapBSidecar, setLapBSidecar] = useState<File | null>(null);
  const [gridStep, setGridStep] = useState("1");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [outcome, setOutcome] = useState<ComparisonWorkflowResponse | null>(null);

  const gridValid = useMemo(() => {
    const value = Number(gridStep);
    return Number.isFinite(value) && value > 0;
  }, [gridStep]);

  const sourcesReady =
    lapACsv !== null &&
    lapASidecar !== null &&
    lapBCsv !== null &&
    lapBSidecar !== null;

  const canSubmit = sourcesReady && gridValid && !loading;

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (
      !canSubmit ||
      lapACsv === null ||
      lapASidecar === null ||
      lapBCsv === null ||
      lapBSidecar === null
    ) {
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await submitComparison({
        lapACsv,
        lapASidecar,
        lapBCsv,
        lapBSidecar,
        gridStep,
      });
      setOutcome(response);
    } catch {
      setError(
        "Could not reach the local OME API. Check that it is running and try again.",
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="app-shell">
      <header className="page-header">
        <p className="eyebrow">Open Motorsport Engineer</p>
        <h1>Compare two laps</h1>
        <p>
          Load two controlled OME CSV lap bundles. OME keeps Lap A as the
          reference, compares Lap B on the accepted distance basis and exposes
          the evidence behind the result.
        </p>
      </header>

      <form className="source-form" onSubmit={handleSubmit}>
        <div className="source-grid">
          <fieldset className="source-group">
            <legend>Lap A</legend>
            <p className="source-group__role">Reference lap</p>
            <SourceFileField
              id="lap-a-csv"
              label="Lap A CSV"
              accept=".csv,text/csv"
              file={lapACsv}
              onChange={setLapACsv}
            />
            <SourceFileField
              id="lap-a-sidecar"
              label="Lap A sidecar"
              accept=".json,application/json"
              file={lapASidecar}
              onChange={setLapASidecar}
            />
          </fieldset>

          <fieldset className="source-group">
            <legend>Lap B</legend>
            <p className="source-group__role">Comparison lap</p>
            <SourceFileField
              id="lap-b-csv"
              label="Lap B CSV"
              accept=".csv,text/csv"
              file={lapBCsv}
              onChange={setLapBCsv}
            />
            <SourceFileField
              id="lap-b-sidecar"
              label="Lap B sidecar"
              accept=".json,application/json"
              file={lapBSidecar}
              onChange={setLapBSidecar}
            />
          </fieldset>
        </div>

        <div className="form-actions">
          <div className="grid-field">
            <label htmlFor="grid-step">Grid step (m)</label>
            <input
              id="grid-step"
              type="number"
              min="0.001"
              step="any"
              value={gridStep}
              aria-invalid={!gridValid}
              aria-describedby="grid-step-help"
              onChange={(event) => setGridStep(event.currentTarget.value)}
            />
            <span id="grid-step-help" className="field-help">
              {gridValid
                ? "Distance spacing used by the deterministic comparison."
                : "Grid step must be greater than zero."}
            </span>
          </div>

          <button className="primary-action" type="submit" disabled={!canSubmit}>
            Compare laps
          </button>
        </div>
      </form>

      {loading ? (
        <div className="status-line" role="status" aria-live="polite">
          Comparing laps…
        </div>
      ) : null}

      {error !== null ? (
        <div className="error-panel" role="alert">
          {error}
        </div>
      ) : null}

      {outcome?.status === "not_ready" ? (
        <WorkflowIssues stage={outcome.stage} issues={outcome.issues} />
      ) : null}

      {outcome?.status === "success" ? (
        <ComparisonResults report={outcome.report} />
      ) : null}
    </main>
  );
}
