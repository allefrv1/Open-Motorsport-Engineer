from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from scripts.check_docs import markdown_target_exists


class DocumentationHarnessTests(unittest.TestCase):
    def test_missing_relative_markdown_target_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "docs" / "README.md"
            source.parent.mkdir(parents=True)
            source.write_text("# Docs\n", encoding="utf-8")

            self.assertFalse(markdown_target_exists(source, "missing.md", root))

    def test_external_link_is_not_treated_as_local_file(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "README.md"
            source.write_text("# Test\n", encoding="utf-8")

            self.assertTrue(markdown_target_exists(source, "https://example.com/resource", root))


if __name__ == "__main__":
    unittest.main()
