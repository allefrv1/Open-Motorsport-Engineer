import { Badge } from "./ui/badge";

export interface EvidenceStatusProps {
  status: string;
  issueCodes: readonly string[];
}

export function evidenceStatusLabel(status: string, issueCodes: readonly string[]): string {
  if (status === "available") return "Available";
  if (
    status === "missing" ||
    status === "missing_evidence" ||
    (status === "not_ready" && issueCodes.includes("missing_channel"))
  ) return "Missing evidence";
  if (status === "not_ready") return "Evidence not ready";
  if (status === "incompatible") return "Incompatible evidence";
  return status;
}

export function EvidenceStatus({ status, issueCodes }: EvidenceStatusProps) {
  const label = evidenceStatusLabel(status, issueCodes);
  const variant = label === "Missing evidence" || label === "Incompatible evidence"
    ? "warning" : label === "Available" ? "outline" : "secondary";
  return <Badge variant={variant}>{label}</Badge>;
}
