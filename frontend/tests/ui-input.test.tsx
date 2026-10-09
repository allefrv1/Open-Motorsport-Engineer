import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Input } from "../src/components/ui/input";

describe("shared input", () => {
  it("preserves its accessible label and validation state", () => {
    render(<><label htmlFor="step">Grid step (m)</label><Input id="step" type="number" min="0.001" aria-invalid="true" /></>);
    const input = screen.getByRole("spinbutton", { name: "Grid step (m)" });
    expect(input).toHaveAttribute("min", "0.001");
    expect(input).toHaveAttribute("aria-invalid", "true");
    expect(input).toHaveClass("ui-input");
  });
});
