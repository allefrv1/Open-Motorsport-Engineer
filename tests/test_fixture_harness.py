from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from scripts.check_fixtures import check_public_fixtures


class FixtureHarnessTests(unittest.TestCase):
    def test_missing_fixture_file_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            fixture_root = root / "fixtures/public"
            license_root = fixture_root / "licenses"
            license_root.mkdir(parents=True)
            (license_root / "test.txt").write_text("license", encoding="utf-8")
            manifest = {
                "fixtures": [
                    {
                        "id": "missing",
                        "path": "missing.csv",
                        "kind": "synthetic",
                        "format_family": "CSV",
                        "source_repository": "https://example.com/repo",
                        "source_path": "missing.csv",
                        "license": "MIT",
                        "license_path": "fixtures/public/licenses/test.txt",
                        "redistribution": "allowed",
                        "purpose": ["negative harness test"],
                    }
                ]
            }
            (fixture_root / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")

            errors = check_public_fixtures(root)

            self.assertTrue(any("fixture file missing" in error for error in errors), errors)


if __name__ == "__main__":
    unittest.main()
