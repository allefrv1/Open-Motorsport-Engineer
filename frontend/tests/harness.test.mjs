import assert from "node:assert/strict";
import test from "node:test";

test("pinned Node runtime is active", () => {
  assert.equal(process.version, "v24.21.0");
});
