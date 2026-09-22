from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from scripts.check_architecture import check_architecture


class ArchitectureHarnessTests(unittest.TestCase):
    def test_forbidden_dependency_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "backend/src/ome/domain").mkdir(parents=True)
            (root / "backend/src/ome/api").mkdir(parents=True)
            (root / "backend/src/ome/domain/bad.py").write_text(
                "from ome.api import routes\n", encoding="utf-8"
            )
            (root / "architecture.toml").write_text(
                "[architecture]\n"
                'root = "backend/src/ome"\n\n'
                "[layers.domain]\n"
                'path = "domain"\n'
                'forbid = ["ome.api"]\n',
                encoding="utf-8",
            )

            errors = check_architecture(root)

            self.assertTrue(
                any("domain may not import ome.api" in error for error in errors),
                errors,
            )


if __name__ == "__main__":
    unittest.main()
