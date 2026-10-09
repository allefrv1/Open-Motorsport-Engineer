"""Real-browser Portland Traqmate QA using the committed fixture and running Compose stack."""

from __future__ import annotations

import os
import re
from pathlib import Path

from playwright.sync_api import Page, expect, sync_playwright

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "fixtures/public/exit-speed/traqmate-portland-laps-4-5.csv"
SCREENSHOTS = ROOT / "artifacts/ui"
BASE_URL = os.environ.get("OME_UI_URL", "http://127.0.0.1:5173")


def assert_plot_click_inspects_exact_sample(page: Page) -> None:
    plot = page.locator(".telemetry-plot")
    page.wait_for_function(
        "el => Boolean(el && el._fullLayout && el.data && el.data.length)",
        arg=plot.element_handle(),
        timeout=30000,
    )
    selected = plot.evaluate(
        """el => {
          const samples = el.data[0].x;
          if (!Array.isArray(samples) || samples.length < 3) {
            throw new Error('Plot contains no inspectable distance samples');
          }
          return samples[2];
        }"""
    )
    cursor = page.get_by_role("slider", name="Inspection distance point")
    expect(cursor).to_have_value("0")
    # Emit using an exact plotted distance, never a fabricated/interpolated one.
    plot.evaluate("(el, x) => el.emit('plotly_click', {points: [{x}]})", selected)
    expect(cursor).to_have_value("2")


def test_real_traqmate_in_browser(page: Page) -> None:
    page.goto(BASE_URL, wait_until="domcontentloaded")
    heading = page.get_by_role("heading", name="Compare two laps")
    expect(heading).to_be_visible()
    eyebrow_box = page.locator(".page-header .eyebrow").bounding_box()
    heading_box = heading.bounding_box()
    assert eyebrow_box is not None and heading_box is not None
    assert abs(eyebrow_box["x"] - heading_box["x"]) < 4, (
        "Page title is visually disconnected from its section label"
    )
    expect(page.get_by_role("region", name="Ready to investigate")).to_be_visible()
    expect(page.get_by_role("button", name="Compare laps")).to_be_disabled()

    page.get_by_role("radio", name="Physical Traqmate").check()
    page.get_by_label("Traqmate telemetry CSV").set_input_files(str(FIXTURE))
    page.get_by_label("Reference source lap").fill("4")
    page.get_by_label("Candidate source lap").fill("5")
    page.get_by_label("Grid step (m)").fill("5")
    page.get_by_role("button", name="Compare laps").click()

    expect(page.get_by_role("heading", name="Lap comparison")).to_be_visible(timeout=60000)
    expect(page.get_by_text("Delta = Lap B - Lap A")).to_be_visible()
    expect(page.get_by_role("heading", name="Synchronized telemetry")).to_be_visible()
    expect(page.get_by_role("heading", name="Supporting evidence")).to_be_visible()
    expect(page.get_by_text("Missing evidence", exact=True).first).to_be_visible()

    assert_plot_click_inspects_exact_sample(page)

    channel = page.get_by_role("checkbox", name=re.compile(r"vehicle\.speed"))
    expect(channel).to_be_checked()
    channel.uncheck()
    expect(channel).not_to_be_checked()
    channel.check()
    expect(channel).to_be_checked()

    plot = page.locator(".telemetry-plot")
    page.get_by_role("button", name="Focus first half").click()
    page.wait_for_function(
        "el => Boolean(el._fullLayout?.xaxis?.range && el._fullLayout.xaxis.range[1] < 2000)",
        arg=plot.element_handle(),
    )
    page.get_by_role("button", name="Reset zoom").click()
    page.wait_for_function(
        "el => Boolean(el._fullLayout?.xaxis?.range && el._fullLayout.xaxis.range[1] > 2500)",
        arg=plot.element_handle(),
    )

    slider = page.get_by_role("slider", name="Inspection distance point")
    slider.focus()
    previous = slider.input_value()
    page.keyboard.press("ArrowRight")
    assert slider.input_value() != previous, "Keyboard cannot advance the sample cursor"

    page.get_by_text("Method and provenance").click()
    expect(page.get_by_text("Algorithm", exact=True)).to_be_visible()
    SCREENSHOTS.mkdir(parents=True, exist_ok=True)
    page.screenshot(
        path=str(SCREENSHOTS / "desktop-traqmate.png"), full_page=True, animations="disabled"
    )

    page.set_viewport_size({"width": 390, "height": 844})
    page.screenshot(
        path=str(SCREENSHOTS / "mobile-traqmate.png"), full_page=True, animations="disabled"
    )
    size = page.evaluate(
        "() => ({viewport: innerWidth, document: document.documentElement.scrollWidth})"
    )
    assert size["document"] <= size["viewport"] + 2, (
        f"Page-level horizontal overflow on mobile: {size}"
    )


def main() -> None:
    assert FIXTURE.is_file(), f"Missing committed telemetry fixture: {FIXTURE}"
    SCREENSHOTS.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1440, "height": 900}, device_scale_factor=1)
        js_errors: list[str] = []
        page.on("pageerror", lambda error: js_errors.append(str(error)))
        try:
            test_real_traqmate_in_browser(page)
            assert not js_errors, f"Uncaught frontend JavaScript errors: {js_errors}"
            print("Browser QA passed: Traqmate, inspection, zoom, evidence and mobile reflow.")
        except Exception:
            page.screenshot(
                path=str(SCREENSHOTS / "failure.png"), full_page=True, animations="disabled"
            )
            raise
        finally:
            browser.close()


if __name__ == "__main__":
    main()
