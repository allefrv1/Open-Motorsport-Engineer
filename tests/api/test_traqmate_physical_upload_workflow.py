from __future__ import annotations

import unittest
from pathlib import Path

from fastapi.testclient import TestClient

from ome.api import create_app

ROOT = Path(__file__).resolve().parents[2]
PORTLAND_FIXTURE = ROOT / "fixtures" / "public" / "exit-speed" / "traqmate-portland-laps-4-5.csv"
OME_FIXTURE = ROOT / "fixtures" / "ome" / "basic-lap.csv"


def physical_files(
    *,
    source: Path = PORTLAND_FIXTURE,
    filename: str = "traqmate-portland-laps-4-5.csv",
) -> dict[str, tuple[str, bytes, str]]:
    return {
        "telemetry_csv": (
            filename,
            source.read_bytes(),
            "text/csv",
        )
    }


def physical_data(
    *,
    reference_lap: int = 4,
    candidate_lap: int = 5,
    grid_step_m: float = 5.0,
) -> dict[str, str]:
    return {
        "reference_lap": str(reference_lap),
        "candidate_lap": str(candidate_lap),
        "grid_step_m": str(grid_step_m),
    }


class Plan030TraqmatePhysicalComparisonHttpWorkflowTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(create_app())

    def post(
        self,
        *,
        source: Path = PORTLAND_FIXTURE,
        filename: str = "traqmate-portland-laps-4-5.csv",
        reference_lap: int = 4,
        candidate_lap: int = 5,
        grid_step_m: float = 5.0,
    ):
        return self.client.post(
            "/api/v1/traqmate/comparison-reports",
            files=physical_files(source=source, filename=filename),
            data=physical_data(
                reference_lap=reference_lap,
                candidate_lap=candidate_lap,
                grid_step_m=grid_step_m,
            ),
        )

    def test_openapi_contains_physical_traqmate_workflow_route(self) -> None:
        response = self.client.get("/openapi.json")

        self.assertEqual(response.status_code, 200)
        self.assertIn(
            "/api/v1/traqmate/comparison-reports",
            response.json()["paths"],
        )

    def test_portland_laps_four_and_five_return_enriched_physical_report(self) -> None:
        response = self.post()

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["status"], "success")

        report = body["report"]
        summaries = {
            item["canonical_concept"]: item["status"] for item in report["supporting_evidence"]
        }

        self.assertEqual(summaries["vehicle.speed"], "available")
        self.assertEqual(summaries["engine.speed"], "available")
        self.assertEqual(summaries["transmission.gear"], "available")
        self.assertEqual(summaries["driver.throttle"], "not_ready")
        self.assertEqual(summaries["driver.brake"], "not_ready")
        self.assertEqual(summaries["driver.steering"], "not_ready")

        self.assertEqual(
            {item["canonical_concept"] for item in report["continuous_overlays"]},
            {"vehicle.speed", "engine.speed"},
        )
        self.assertIsNotNone(report["gear_overlay"])
        self.assertGreater(len(report["comparison"]["distance_grid_m"]), 100)
        self.assertEqual(
            len(report["comparison"]["distance_grid_m"]),
            len(report["comparison"]["delta_b_vs_a_s"]),
        )

    def test_analysis_context_is_dataset_linked_and_preserves_explicit_lap_order(self) -> None:
        response = self.post()

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["status"], "success")

        base = body["report"]["provenance"]["base_comparison"]
        context_a = base["lap_a"]["context"]
        context_b = base["lap_b"]["context"]

        self.assertEqual(context_a["dataset_fingerprint"], context_b["dataset_fingerprint"])
        self.assertEqual(
            context_a["session_identifier"],
            f"dataset:{context_a['dataset_fingerprint']}",
        )
        self.assertEqual(context_b["session_identifier"], context_a["session_identifier"])
        self.assertIsNone(context_a["run_identifier"])
        self.assertIsNone(context_b["run_identifier"])
        self.assertEqual(context_a["lap_identifier"], "source-lap:4")
        self.assertEqual(context_b["lap_identifier"], "source-lap:5")

    def test_caller_can_reverse_reference_and_candidate_without_automatic_ranking(self) -> None:
        response = self.post(reference_lap=5, candidate_lap=4)

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["status"], "success")

        base = body["report"]["provenance"]["base_comparison"]
        self.assertEqual(base["lap_a"]["context"]["lap_identifier"], "source-lap:5")
        self.assertEqual(base["lap_b"]["context"]["lap_identifier"], "source-lap:4")

    def test_unknown_source_lap_is_lap_window_not_ready(self) -> None:
        response = self.post(candidate_lap=99)

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["status"], "not_ready")
        self.assertEqual(body["stage"], "lap_window")
        self.assertIn(
            "missing_lap_marker",
            {issue["code"] for issue in body["issues"]},
        )

    def test_same_source_lap_is_track_reference_not_ready(self) -> None:
        response = self.post(reference_lap=4, candidate_lap=4)

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["status"], "not_ready")
        self.assertEqual(body["stage"], "track_reference")
        self.assertIn(
            "same_lap_window",
            {issue["code"] for issue in body["issues"]},
        )

    def test_invalid_source_is_import_not_ready(self) -> None:
        response = self.post(source=OME_FIXTURE, filename="not-traqmate.csv")

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["status"], "not_ready")
        self.assertEqual(body["stage"], "import")
        self.assertIn(
            body["issues"][0]["code"],
            {"invalid_profile", "unsupported_source"},
        )

    def test_non_positive_grid_step_is_comparison_preparation_not_ready(self) -> None:
        response = self.post(grid_step_m=0.0)

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["status"], "not_ready")
        self.assertEqual(body["stage"], "comparison_preparation")
        self.assertIn(
            "invalid_grid_step",
            {issue["code"] for issue in body["issues"]},
        )

    def test_missing_required_form_field_returns_422(self) -> None:
        response = self.client.post(
            "/api/v1/traqmate/comparison-reports",
            files=physical_files(),
            data={
                "reference_lap": "4",
                "grid_step_m": "5.0",
            },
        )

        self.assertEqual(response.status_code, 422)

    def test_client_filename_cannot_escape_staging_or_leak_server_paths(self) -> None:
        response = self.post(filename="../../portland.csv")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "success")
        serialized = response.text
        self.assertNotIn("../", serialized)
        self.assertNotIn("/tmp/", serialized)
        self.assertNotIn("\\tmp\\", serialized)

    def test_equivalent_requests_are_deterministic(self) -> None:
        first = self.post()
        second = self.post()

        self.assertEqual(first.status_code, 200)
        self.assertEqual(second.status_code, 200)
        self.assertEqual(first.json(), second.json())


if __name__ == "__main__":
    unittest.main()
