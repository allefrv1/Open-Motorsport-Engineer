import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { EvidenceStatus } from "../src/components/EvidenceStatus";

describe("evidence status presentation", () => {
  it("calls missing_channel a missing evidence item", () => {
    render(<EvidenceStatus status="not_ready" issueCodes={["missing_channel"]} />);
    expect(screen.getByText("Missing evidence")).toHaveClass("ui-badge--warning");
  });

  it("does not confuse unrelated not-ready evidence with missing evidence", () => {
    render(<EvidenceStatus status="not_ready" issueCodes={["validation_error"]} />);
    expect(screen.getByText("Evidence not ready")).toBeVisible();
    expect(screen.queryByText("Missing evidence")).toBeNull();
  });

  it("shows available and incompatible statuses as explicit text", () => {
    const { rerender } = render(<EvidenceStatus status="available" issueCodes={[]} />);
    expect(screen.getByText("Available")).toBeVisible();
    rerender(<EvidenceStatus status="incompatible" issueCodes={[]} />);
    expect(screen.getByText("Incompatible evidence")).toBeVisible();
  });
});
