export interface WorkflowIssue {
  code: string;
  message: string;
  lap_side: string | null;
  canonical_concept: string | null;
}

export interface LapEvidenceContext {
  dataset_fingerprint: string;
  session_identifier: string;
  run_identifier: string | null;
  lap_identifier: string;
}

export interface CanonicalSeriesEvidence {
  dataset_fingerprint: string;
  source_channel_identifier: string;
  source_original_name: string;
  canonical_concept: string;
  unit: string;
  semantic_id: string | null;
}

export interface ComparisonLapEvidence {
  context: LapEvidenceContext;
  distance: CanonicalSeriesEvidence;
  elapsed_time: CanonicalSeriesEvidence;
}

export interface ComparisonProvenance {
  algorithm_id: string;
  algorithm_version: string;
  parameters: Record<string, unknown>;
  reference_concept: string;
  reference_unit: string;
  time_concept: string;
  time_unit: string;
  common_start_m: number;
  common_end_m: number;
  lap_a: ComparisonLapEvidence;
  lap_b: ComparisonLapEvidence;
}

export interface LapComparisonReport {
  reference_concept: string;
  reference_unit: string;
  time_concept: string;
  time_unit: string;
  common_start_m: number;
  common_end_m: number;
  distance_grid_m: number[];
  lap_a_elapsed_s: number[];
  lap_b_elapsed_s: number[];
  delta_b_vs_a_s: number[];
  provenance: ComparisonProvenance;
}

export interface DeltaRegion {
  kind: string;
  start_distance_m: number;
  end_distance_m: number;
  start_delta_s: number;
  end_delta_s: number;
  total_delta_change_s: number;
  interval_count: number;
}

export interface SupportingEvidence {
  canonical_concept: string;
  kind: string;
  status: string;
  unit: string | null;
  issue_codes: string[];
  messages: string[];
}

export interface ContinuousOverlay {
  canonical_concept: string;
  unit: string;
  distance_grid_m: number[];
  lap_a_values: number[];
  lap_b_values: number[];
}

export interface GearOverlay {
  canonical_concept: string;
  unit: string;
  distance_grid_m: number[];
  lap_a_gears: number[];
  lap_b_gears: number[];
}

export interface ComparisonReport {
  comparison: LapComparisonReport;
  observations: {
    regions: DeltaRegion[];
  };
  continuous_overlays: ContinuousOverlay[];
  gear_overlay: GearOverlay | null;
  supporting_evidence: SupportingEvidence[];
  provenance: {
    assembler_id: string;
    assembler_version: string;
    requested_concepts: string[];
  };
}

export type ComparisonWorkflowResponse =
  | {
      status: "success";
      report: ComparisonReport;
    }
  | {
      status: "not_ready";
      stage: "import" | "preparation" | "report";
      issues: WorkflowIssue[];
    };

export interface ComparisonUpload {
  lapACsv: File;
  lapASidecar: File;
  lapBCsv: File;
  lapBSidecar: File;
  gridStep: string;
}

export async function submitComparison(
  upload: ComparisonUpload,
): Promise<ComparisonWorkflowResponse> {
  const body = new FormData();
  body.append("lap_a_csv", upload.lapACsv);
  body.append("lap_a_sidecar", upload.lapASidecar);
  body.append("lap_b_csv", upload.lapBCsv);
  body.append("lap_b_sidecar", upload.lapBSidecar);
  body.append("grid_step_m", upload.gridStep);

  const response = await fetch("/api/v1/ome-csv/comparison-reports", {
    method: "POST",
    body,
  });

  if (!response.ok) {
    throw new Error(`OME API request failed with HTTP ${response.status}.`);
  }

  const payload = (await response.json()) as Partial<ComparisonWorkflowResponse>;

  if (payload.status !== "success" && payload.status !== "not_ready") {
    throw new Error("OME API returned an unsupported response.");
  }

  return payload as ComparisonWorkflowResponse;
}
