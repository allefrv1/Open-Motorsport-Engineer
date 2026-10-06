from __future__ import annotations

import csv
import io
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi import UploadFile
from fastapi.testclient import TestClient

from ome.api import create_app
from ome.api.models import ComparisonReportSuccessDto
from ome.api.upload_workflow import stage_single_csv_upload as real_stage_single_csv_upload
from ome.application import (
    ComparisonReportIssueCode,
    ComparisonReportNotReady,
    ComparisonReportOutcome,
    ComparisonReportReadinessIssue,
    ComparisonReportRequest,
    ComparisonReportService,
    ComparisonReportSuccess,
)

ROOT = Path(__file__).resolve().parents[2]
PORTLAND_FIXTURE = ROOT / "fixtures" / "public" / "exit-speed" / "traqmate-portland-laps-4-5.csv"
OME_FIXTURE = ROOT / "fixtures" / "ome" / "basic-lap.csv"


class _RecordingReportService:
    def __init__(self) -> None:
        self._delegate = ComparisonReportService()
        self.outcomes: list[ComparisonReportOutcome] = []

    def build(self, request: ComparisonReportRequest) -> ComparisonReportOutcome:
        outcome = self._delegate.build(request)
        self.outcomes.append(outcome)
        return outcome


class _NotReadyReportService:
    def build(self, request: ComparisonReportRequest) -> ComparisonReportOutcome:
        del request
        return ComparisonReportNotReady(
            issues=(
                ComparisonReportReadinessIssue(
                    code=ComparisonReportIssueCode.OBSERVATIONS_NOT_READY,
                    message="Forced report not-ready for transport-stage verification.",
                ),
            )
        )


def physical_files(
    *,
    source: Path = PORTLAND_FIXTURE,
    filename: str = "traqmate-portland-laps-4-5.csv",
    payload: bytes | None = None,
) -> dict[str, tuple[str, bytes, str]]:
    return {
        "telemetry_csv": (
            filename,
            source.read_bytes() if payload is None else payload,
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


def source_with_cell_replaced(
    channel_identifier: str,
    replacement: str,
) -> bytes:
    lines = PORTLAND_FIXTURE.read_text(encoding="utf-8").splitlines()

    header_index: int | None = None
    headers: list[str] | None = None
    for index, line in enumerate(lines):
        row = next(csv.reader([line]))
        normalized_headers = [cell.strip() for cell in row]
        if "Elapsed Time" in normalized_headers and channel_identifier in normalized_headers:
            header_index = index
            headers = row
            break

    if header_index is None or headers is None:
        raise AssertionError(f"Source channel {channel_identifier!r} was not found in fixture.")

    channel_index = [cell.strip() for cell in headers].index(channel_identifier)
    for index in range(header_index + 1, len(lines)):
        row = next(csv.reader([lines[index]]))
        if len(row) != len(headers) or not row[channel_index].strip():
            continue

        row[channel_index] = replacement
        buffer = io.StringIO()
        csv.writer(buffer, lineterminator="").writerow(row)
        lines[index] = buffer.getvalue()
        return ("\n".join(lines) + "\n").encode("utf-8")

    raise AssertionError(f"Source channel {channel_identifier!r} had no replaceable fixture value.")


class Plan030TraqmatePhysicalComparisonHttpWorkflowTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(create_app())

    def post(
        self,
        *,
        source: Path = PORTLAND_FIXTURE,
        filename: str = "traqmate-portland-laps-4-5.csv",
        payload: bytes | None = None,
        reference_lap: int = 4,
        candidate_lap: int = 5,
        grid_step_m: float = 5.0,
        client: TestClient | None = None,
    ):
        active_client = self.client if client is None else client
        return active_client.post(
            "/api/v1/traqmate/comparison-reports",
            files=physical_files(
                source=source,
                filename=filename,
                payload=payload,
            ),
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
        source_before = PORTLAND_FIXTURE.read_bytes()
        recorder = _RecordingReportService()
        client = TestClient(create_app(report_service=recorder))

        response = self.post(client=client)

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["status"], "success")
        self.assertEqual(PORTLAND_FIXTURE.read_bytes(), source_before)

        self.assertEqual(len(recorder.outcomes), 1)
        core_outcome = recorder.outcomes[0]
        self.assertIsInstance(core_outcome, ComparisonReportSuccess)
        assert isinstance(core_outcome, ComparisonReportSuccess)
        self.assertEqual(
            body["report"],
            ComparisonReportSuccessDto.from_domain(core_outcome).model_dump(mode="json"),
        )

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

    def test_invalid_rpm_evidence_is_supporting_evidence_not_ready(self) -> None:
        response = self.post(
            payload=source_with_cell_replaced(
                "RPMs",
                "not-a-number",
            )
        )

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["status"], "not_ready")
        self.assertEqual(body["stage"], "supporting_evidence")
        self.assertIn(
            "normalization_not_ready",
            {issue["code"] for issue in body["issues"]},
        )

    def test_report_failure_retains_report_stage(self) -> None:
        client = TestClient(create_app(report_service=_NotReadyReportService()))

        response = self.post(client=client)

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["status"], "not_ready")
        self.assertEqual(body["stage"], "report")
        self.assertEqual(body["issues"][0]["code"], "observations_not_ready")

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
        staged_paths: list[Path] = []

        def tracking_stage(
            root: Path,
            *,
            csv_upload: UploadFile,
            fallback: str = "telemetry.csv",
        ) -> Path:
            staged = real_stage_single_csv_upload(
                root,
                csv_upload=csv_upload,
                fallback=fallback,
            )
            staged_paths.append(staged)
            return staged

        with patch(
            "ome.api.app.stage_single_csv_upload",
            side_effect=tracking_stage,
        ):
            response = self.post(filename="../../portland.csv")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "success")
        serialized = response.text
        self.assertNotIn("../", serialized)
        self.assertNotIn("/tmp/", serialized)
        self.assertNotIn("\\tmp\\", serialized)

        self.assertEqual(len(staged_paths), 1)
        self.assertEqual(staged_paths[0].name, "portland.csv")
        self.assertFalse(staged_paths[0].exists())
        self.assertFalse(staged_paths[0].parent.exists())

    def test_equivalent_requests_are_deterministic(self) -> None:
        first = self.post()
        second = self.post()

        self.assertEqual(first.status_code, 200)
        self.assertEqual(second.status_code, 200)
        self.assertEqual(first.json(), second.json())


if __name__ == "__main__":
    unittest.main()
