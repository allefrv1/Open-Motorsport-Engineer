import assert from "node:assert/strict";
import { readdirSync, readFileSync } from "node:fs";
import { dirname, join, relative } from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

const TEST_DIR = dirname(fileURLToPath(import.meta.url));
const SRC_DIR = join(TEST_DIR, "..", "src");

function sourceFiles(directory) {
  return readdirSync(directory, { withFileTypes: true }).flatMap((entry) => {
    const path = join(directory, entry.name);
    if (entry.isDirectory()) {
      return sourceFiles(path);
    }
    return /\.(ts|tsx)$/.test(entry.name) ? [path] : [];
  });
}

test("pinned Node runtime is active", () => {
  assert.equal(process.version, "v24.21.0");
});

test("Plotly stays isolated behind the visualization adapter", () => {
  const importers = sourceFiles(SRC_DIR)
    .filter((path) => readFileSync(path, "utf8").includes("plotly.js-dist-min"))
    .map((path) => relative(SRC_DIR, path).replaceAll("\\", "/"));

  assert.deepEqual(importers, ["PlotlyTelemetryFigure.tsx"]);
});
