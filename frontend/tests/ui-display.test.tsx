import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Badge } from "../src/components/ui/badge";
import { Card, CardContent, CardHeader } from "../src/components/ui/card";

describe("shared display primitives", () => {
  it("renders a semantic region for an investigation card", () => {
    render(
      <Card aria-label="Ready to investigate">
        <CardHeader><h2>Investigation</h2></CardHeader>
        <CardContent>Measured data only</CardContent>
      </Card>,
    );
    expect(screen.getByRole("region", { name: "Ready to investigate" })).toHaveClass("ui-card");
    expect(screen.getByText("Measured data only")).toBeVisible();
  });

  it("keeps missing evidence visible in text instead of relying on color", () => {
    render(<Badge variant="warning">Missing evidence</Badge>);
    expect(screen.getByText("Missing evidence")).toHaveClass("ui-badge--warning");
  });
});
