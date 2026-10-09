import { FormEvent, useMemo, useState } from "react";

import {
  ComparisonReport,
  ComparisonWorkflowResponse,
  ComparisonWorkflowStage,
  SupportingEvidence,
  WorkflowIssue,
  submitComparison,
  submitTraqmateComparison,
} from "./api";
import { DeltaChart } from "./DeltaChart";
import { Button } from "./components/ui/button";
import { Badge } from "./components/ui/badge";
import { Card } from "./components/ui/card";
import { TelemetryInvestigationPlots } from "./TelemetryInvestigationPlots";

type SourceWorkflow = "ome_csv" | "traqmate";

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
  if (
    item.status === "missing" ||
    item.status === "missing_evidence" ||
    (item.status === "not_ready" && item.issue_codes.includes("missing_channel"))
  ) {
    return "Missing evidence";
  }
  if (item.status === "not_ready") {
    return "Evidence not ready";
  }
  if (item.status === "incompatible") {
    return "Incompatible evidence";
  }
  return item.status;
}

function stageLabel(stage: ComparisonWorkflowStage): string {
  const label = stage.replaceAll("_", " ");
  return label.charAt(0).toUpperCase() + label.slice(1);
}

function isPositiveIntegerInput(value: string): boolean {
  if (value.trim() === "") {
    return false;
  }
  const number = Number(value);
  return Number.isInteger(number) && number > 0;
}

function WorkflowIssues({
  stage,
  issues,
}: {
  stage: ComparisonWorkflowStage;
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

function ComparisonResults({ report }: { report: ComparisonReport }) {
  const [showAllObservations, setShowAllObservations] = useState(false);
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
          <p className="eyebrow">Analysis ready · Derived metric</p>
          <h2 id="comparison-result-heading">Lap comparison</h2>
          <div className="comparison-meta" aria-label="Comparison method summary">
            <span>Lap A = reference</span>
            <span>Delta = Lap B - Lap A</span>
            <span>Reference: {provenance.lap_a.context.lap_identifier}</span>
            <span>Candidate: {provenance.lap_b.context.lap_identifier}</span>
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

      <section className="result-section result-section--overview" aria-labelledby="delta-heading">
        <h2 id="delta-heading">Delta over distance</h2>
        <DeltaChart
          distances={comparison.distance_grid_m}
          deltas={comparison.delta_b_vs_a_s}
        />
      </section>

      <TelemetryInvestigationPlots report={report} />

      <div className="analysis-lower-grid">
      <section className="result-section" aria-labelledby="observations-heading">
        <div className="lower-section-header">
          <div>
            <p className="eyebrow">Server-returned regions</p>
            <h2 id="observations-heading">Observations</h2>
          </div>
          <span className="count-pill">{report.observations.regions.length} regions</span>
        </div>
        <p className="analysis-note">Gain/loss observations are not causal diagnoses.</p>
        {report.observations.regions.length === 0 ? (
          <p>No gain/loss regions were returned by the deterministic observation layer.</p>
        ) : (
          <ul className="observation-list">
            {(showAllObservations
              ? report.observations.regions
              : report.observations.regions.slice(0, 7)
            ).map((region, index) => (
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
        {report.observations.regions.length > 7 ? (
          <Button
            type="button"
            variant="outline"
            className="secondary-action observations-toggle"
            onClick={() => setShowAllObservations((current) => !current)}
          >
            {showAllObservations
              ? "Show fewer observations"
              : `Show all ${report.observations.regions.length} observations`}
          </Button>
        ) : null}
      </section>

      <section className="result-section" aria-labelledby="evidence-heading">
        <div className="lower-section-header">
          <div>
            <p className="eyebrow">Available and missing channels</p>
            <h2 id="evidence-heading">Supporting evidence</h2>
          </div>
          <span className="count-pill">{report.supporting_evidence.length} concepts</span>
        </div>
        <ul className="evidence-list">
          {report.supporting_evidence.map((item) => (
            <li
              className={item.status === "available"
                ? "evidence-item"
                : "evidence-item evidence-item--missing"}
              key={item.canonical_concept}
            >
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
      </div>

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
  const [workflow, setWorkflow] = useState<SourceWorkflow>("ome_csv");
  const [lapACsv, setLapACsv] = useState<File | null>(null);
  const [lapASidecar, setLapASidecar] = useState<File | null>(null);
  const [lapBCsv, setLapBCsv] = useState<File | null>(null);
  const [lapBSidecar, setLapBSidecar] = useState<File | null>(null);
  const [traqmateCsv, setTraqmateCsv] = useState<File | null>(null);
  const [referenceLap, setReferenceLap] = useState("");
  const [candidateLap, setCandidateLap] = useState("");
  const [gridStep, setGridStep] = useState("1");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [outcome, setOutcome] = useState<ComparisonWorkflowResponse | null>(null);

  const gridValid = useMemo(() => {
    const value = Number(gridStep);
    return Number.isFinite(value) && value > 0;
  }, [gridStep]);

  const referenceLapValid = isPositiveIntegerInput(referenceLap);
  const candidateLapValid = isPositiveIntegerInput(candidateLap);

  const omeSourcesReady =
    lapACsv !== null &&
    lapASidecar !== null &&
    lapBCsv !== null &&
    lapBSidecar !== null;

  const traqmateSourcesReady =
    traqmateCsv !== null && referenceLapValid && candidateLapValid;

  const sourcesReady =
    workflow === "ome_csv" ? omeSourcesReady : traqmateSourcesReady;

  const canSubmit = sourcesReady && gridValid && !loading;

  function changeWorkflow(next: SourceWorkflow) {
    if (next === workflow) {
      return;
    }

    setWorkflow(next);
    setError(null);
    setOutcome(null);

    if (next === "traqmate") {
      setLapACsv(null);
      setLapASidecar(null);
      setLapBCsv(null);
      setLapBSidecar(null);
    } else {
      setTraqmateCsv(null);
      setReferenceLap("");
      setCandidateLap("");
    }
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (!canSubmit) {
      return;
    }

    setLoading(true);
    setError(null);

    try {
      let response: ComparisonWorkflowResponse;

      if (workflow === "ome_csv") {
        if (
          lapACsv === null ||
          lapASidecar === null ||
          lapBCsv === null ||
          lapBSidecar === null
        ) {
          return;
        }

        response = await submitComparison({
          lapACsv,
          lapASidecar,
          lapBCsv,
          lapBSidecar,
          gridStep,
        });
      } else {
        if (
          traqmateCsv === null ||
          !referenceLapValid ||
          !candidateLapValid
        ) {
          return;
        }

        response = await submitTraqmateComparison({
          telemetryCsv: traqmateCsv,
          referenceLap,
          candidateLap,
          gridStep,
        });
      }

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
      <div className="app-topbar">
        <div className="brand-lockup">
          <span className="brand-mark" aria-hidden="true">OME</span>
          <span>Open Motorsport Engineer <small>Local engineering workspace</small></span>
        </div>
        <Badge variant="outline" className="app-topbar__state">Evidence-first analysis</Badge>
      </div>
      <header className="page-header">
        <div className="page-header__heading">
          <p className="eyebrow">Workspace / Lap analysis</p>
          <h1>Compare two laps</h1>
        </div>
        <p>
          Choose a supported source workflow, keep the reference/candidate order
          explicit and investigate the same deterministic evidence model across
          controlled and physical telemetry.
        </p>
      </header>

      <div className="workspace-layout">
      <aside className="setup-pane" aria-label="Source setup">
        <div className="pane-heading">
          <p className="eyebrow">01 / Prepare</p>
          <h2>Source setup</h2>
          <p>Select measured source data and keep lap order explicit.</p>
        </div>
      <form className="source-form" onSubmit={handleSubmit}>
        <fieldset className="workflow-selector">
          <legend>Source workflow</legend>
          <div className="workflow-options">
            <div className="workflow-option">
              <input
                id="workflow-ome-csv"
                type="radio"
                name="source-workflow"
                value="ome_csv"
                checked={workflow === "ome_csv"}
                disabled={loading}
                onChange={() => changeWorkflow("ome_csv")}
              />
              <div>
                <label htmlFor="workflow-ome-csv">Controlled OME CSV</label>
                <p>Two prepared lap bundles with explicit sidecars.</p>
              </div>
            </div>

            <div className="workflow-option">
              <input
                id="workflow-traqmate"
                type="radio"
                name="source-workflow"
                value="traqmate"
                checked={workflow === "traqmate"}
                disabled={loading}
                onChange={() => changeWorkflow("traqmate")}
              />
              <div>
                <label htmlFor="workflow-traqmate">Physical Traqmate</label>
                <p>One Trackvision V2 source with caller-selected source laps.</p>
              </div>
            </div>
          </div>
        </fieldset>

        {workflow === "ome_csv" ? (
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
        ) : (
          <div className="source-grid">
            <fieldset className="source-group">
              <legend>Physical source</legend>
              <p className="source-group__role">Traqmate Trackvision V2</p>
              <SourceFileField
                id="traqmate-csv"
                label="Traqmate telemetry CSV"
                accept=".csv,text/csv"
                file={traqmateCsv}
                onChange={setTraqmateCsv}
              />
            </fieldset>

            <fieldset className="source-group">
              <legend>Source laps</legend>
              <p className="source-group__role">
                Explicit caller order. OME does not rank or auto-select laps.
              </p>

              <div className="lap-inputs">
                <div className="grid-field grid-field--full">
                  <label htmlFor="reference-source-lap">
                    Reference source lap
                  </label>
                  <input
                    id="reference-source-lap"
                    type="number"
                    min="1"
                    step="1"
                    inputMode="numeric"
                    value={referenceLap}
                    aria-invalid={
                      referenceLap !== "" && !referenceLapValid
                    }
                    aria-describedby="reference-source-lap-help"
                    onChange={(event) =>
                      setReferenceLap(event.currentTarget.value)
                    }
                  />
                  <span
                    id="reference-source-lap-help"
                    className="field-help"
                  >
                    Positive integer. This becomes Lap A, the reference.
                  </span>
                </div>

                <div className="grid-field grid-field--full">
                  <label htmlFor="candidate-source-lap">
                    Candidate source lap
                  </label>
                  <input
                    id="candidate-source-lap"
                    type="number"
                    min="1"
                    step="1"
                    inputMode="numeric"
                    value={candidateLap}
                    aria-invalid={
                      candidateLap !== "" && !candidateLapValid
                    }
                    aria-describedby="candidate-source-lap-help"
                    onChange={(event) =>
                      setCandidateLap(event.currentTarget.value)
                    }
                  />
                  <span
                    id="candidate-source-lap-help"
                    className="field-help"
                  >
                    Positive integer. This becomes Lap B, the comparison.
                  </span>
                </div>
              </div>
            </fieldset>
          </div>
        )}

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

          <Button className="primary-action" type="submit" disabled={!canSubmit}>
            Compare laps
          </Button>
        </div>
      </form>
      </aside>

      <div className="analysis-pane" aria-label="Engineering investigation">
      {outcome === null && !loading && error === null ? (
        <Card className="empty-workspace" aria-label="Ready to investigate">
          <span className="empty-workspace__eyebrow">02 / Investigate</span>
          <div className="empty-workspace__visual" aria-hidden="true">
            <span />
            <span />
            <span />
          </div>
          <h2>Your telemetry investigation starts here</h2>
          <p>
            Select a source, specify Lap A and Lap B, then compare. Verified
            metrics, synchronized channels, exact samples and provenance will
            appear in this workspace.
          </p>
          <p className="empty-workspace__hint">
            No demonstration values or missing channels are invented.
          </p>
        </Card>
      ) : null}

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
      </div>
      </div>
    </main>
  );
}
