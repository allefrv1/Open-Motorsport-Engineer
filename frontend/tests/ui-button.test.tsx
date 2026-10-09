import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Button } from "../src/components/ui/button";

describe("shared interface button", () => {
  it("preserves native disabled and accessible button semantics", () => {
    render(<Button disabled>Compare laps</Button>);
    const button = screen.getByRole("button", { name: "Compare laps" });
    expect(button).toBeDisabled();
    expect(button).toHaveClass("ui-button", "ui-button--default");
  });

  it("supports secondary variants and native click handlers", () => {
    let clicks = 0;
    render(<Button variant="outline" onClick={() => { clicks += 1; }}>Show observations</Button>);
    screen.getByRole("button", { name: "Show observations" }).click();
    expect(clicks).toBe(1);
  });
});
