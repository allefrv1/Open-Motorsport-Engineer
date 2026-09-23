from __future__ import annotations

import unittest
from pathlib import Path

from fastapi.testclient import TestClient

from ome.api import create_app

ROOT = Path(__file__).resolve().parents[2]
LAP_A_CSV = ROOT / "fixtures" / "ome" / "mvp-comparison-lap-a.csv"
LAP_A_SIDECAR = ROOT / "fixtures" / "ome" / "mvp-comparison-lap-a.ome.json"
LAP_B_CSV = ROOT / "fixtures" / "ome" / "mvp-comparison-lap-b.csv"
LAP_B_SIDECAR = ROOT / "fixtures" / "ome" / "mvp-comparison-lap-b.ome.json"
BASIC_CSV = ROOT / "fixtures" / "ome" / "basic-lap.csv"
BASIC_SIDECAR = ROOT / "fixtures" / "ome" / "basic-lap.ome.json"


def files_for(
    *,
    lap_a_csv: Path = LAP_A_CSV,
    lap_a_sidecar: Path = LAP_A_SIDECAR,
    lap_b_csv: Path = LAP_B_CSV,
    lap_b_sidecar: Path = LAP_B_SIDECAR,
    lap_a_name: str = "mvp-comparison-lap-a.csv",
    lap_b_name: str = "mvp-comparison-lap-b.csv",
) -> dict[str, tuple[str, bytes, str]]:
    return {
        "lap_a_csv": (lap_a_name, lap_a_csv.read_bytes(), "text/csv"),
        "lap_a_sidecar": (
            "mvp-comparison-lap-a.ome.json",
            lap_a_sidecar.read_bytes(),
            "application/json",
        ),
        "lap_b_csv": (lap_b_name, lap_b_csv.read_bytes(), "text/csv"),
        "lap_b_sidecar": (
            "mvp-comparison-lap-b.ome.json",
            lap_b_sidecar.read_bytes(),
            "application/json",
        ),
    }


class Plan017OmeCsvUploadApiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(create_app())

    def test_controlled_ome_csv_uploads_return_known_comparison_report(self) -> None:
        response = self.client.post(
            "/api/v1/ome-csv/comparison-reports",
            files=files_for(),
            data={"grid_step_m": "25.0"},
        )

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["status"], "success")

        report = body["report"]
        self.assertEqual(
            report["comparison"]["distance_grid_m"],
            [0.0, 25.0, 50.0, 75.0, 100.0],
        )
        self.assertAlmostEqual(report["comparison"]["delta_b_vs_a_s"][-1], 0.20)
        self.assertEqual(
            report["provenance"]["base_comparison"]["lap_a"]["distance"][
                "source_channel_identifier"
            ],
            "lap_distance_src",
        )
        self.assertEqual(
            report["provenance"]["base_comparison"]["lap_a"]["elapsed_time"][
                "source_channel_identifier"
            ],
            "time_s",
        )
        self.assertTrue(
            report["provenance"]["base_comparison"]["lap_a"]["context"][
                "session_identifier"
            ].startswith("session:")
        )

    def test_missing_distance_is_preparation_not_ready(self) -> None:
        response = self.client.post(
            "/api/v1/ome-csv/comparison-reports",
            files=files_for(
                lap_b_csv=BASIC_CSV,
                lap_b_sidecar=BASIC_SIDECAR,
                lap_b_name="basic-lap.csv",
            ),
            data={"grid_step_m": "25.0"},
        )

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["status"], "not_ready")
        self.assertEqual(body["stage"], "preparation")
        self.assertIn("missing_lap_distance", [issue["code"] for issue in body["issues"]])
        self.assertIn("b", [issue["lap_side"] for issue in body["issues"]])

    def test_invalid_sidecar_is_import_not_ready(self) -> None:
        files = files_for()
        files["lap_b_sidecar"] = (
            "mvp-comparison-lap-b.ome.json",
            b'{"ome_csv_version":"99"}',
            "application/json",
        )

        response = self.client.post(
            "/api/v1/ome-csv/comparison-reports",
            files=files,
            data={"grid_step_m": "25.0"},
        )

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["status"], "not_ready")
        self.assertEqual(body["stage"], "import")
        self.assertEqual(body["issues"][0]["lap_side"], "b")
        self.assertEqual(body["issues"][0]["code"], "invalid_profile")

    def test_missing_required_multipart_part_returns_422(self) -> None:
        files = files_for()
        del files["lap_b_sidecar"]

        response = self.client.post(
            "/api/v1/ome-csv/comparison-reports",
            files=files,
        )

        self.assertEqual(response.status_code, 422)

    def test_invalid_grid_step_transport_value_returns_422(self) -> None:
        response = self.client.post(
            "/api/v1/ome-csv/comparison-reports",
            files=files_for(),
            data={"grid_step_m": "not-a-number"},
        )

        self.assertEqual(response.status_code, 422)

    def test_client_filenames_cannot_escape_staging_or_leak_paths(self) -> None:
        response = self.client.post(
            "/api/v1/ome-csv/comparison-reports",
            files=files_for(
                lap_a_name="../../mvp-comparison-lap-a.csv",
                lap_b_name=r"..\..\mvp-comparison-lap-b.csv",
            ),
            data={"grid_step_m": "25.0"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "success")
        serialized = response.text
        self.assertNotIn("../", serialized)
        self.assertNotIn("..\\\\", serialized)
        self.assertNotIn("/tmp/", serialized)

    def test_openapi_contains_source_workflow_route(self) -> None:
        response = self.client.get("/openapi.json")

        self.assertEqual(response.status_code, 200)
        self.assertIn(
            "/api/v1/ome-csv/comparison-reports",
            response.json()["paths"],
        )


if __name__ == "__main__":
    unittest.main()
