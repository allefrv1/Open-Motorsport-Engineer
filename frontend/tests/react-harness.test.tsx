import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

function HarnessProbe() {
  return <div role="status">React test harness ready</div>;
}

describe("frontend React harness", () => {
  it("renders through jsdom and React Testing Library", () => {
    render(<HarnessProbe />);

    expect(screen.getByRole("status").textContent).toBe("React test harness ready");
  });
});
