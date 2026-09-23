from __future__ import annotations

import unittest

from fastapi.testclient import TestClient

from ome.application import (
    ComparisonReportIssueCode,
    ComparisonReportNotReady,
    ComparisonReportReadinessIssue,
    ComparisonReportRequest,
)
from ome.api import create_app


def _evidence(
    *,
    dataset_fingerprint: str,
    source_channel_identifier: str,
    source_original_name: str,
    canonical_concept: str,
    unit: str,
    semantic_id: str | None = None,
) -> dict[str, object]:
    return {
        "dataset_fingerprint": dataset_fingerprint,
        "source_channel_identifier": source_channel_identifier,
        "source_original_name": source_original_name,
        "canonical_concept": canonical_concept,
        "unit": unit,
        "semantic_id": semantic_id,
        "transformations": [
            {
                "transformation_id": "test.normalization",
                "transformation_version": "0.1.0",
                "parameters": {},
            }
        ],
    }


def _lap_payload(
    *,
    fingerprint: str,
    session: str,
    run: str,
    lap: str,
    distance: list[float] | None,
    elapsed: list[float] | None,
) -> dict[str, object]:
    return {
        "context": {
            "dataset_fingerprint": fingerprint,
            "session_identifier": session,
            "run_identifier": run,
            "lap_identifier": lap,
        },
        "distance": None
        if distance is None
        else {
            "values": distance,
            "evidence": _evidence(
                dataset_fingerprint=fingerprint,
                source_channel_identifier="distance",
                source_original_name="Distance",
                canonical_concept="lap.distance",
                unit="m",
            ),
        },
        "elapsed_time": None
        if elapsed is None
        else {
            "values": elapsed,
            "evidence": _evidence(
                dataset_fingerprint=fingerprint,
                source_channel_identifier="time",
                source_original_name="Time",
                canonical_concept="time.elapsed",
                unit="s",
            ),
        },
    }


def _success_payload() -> dict[str, object]:
    return {
        "comparison": {
            "lap_a": _lap_payload(
                fingerprint="sha256:lap-a",
                session="session-a",
                run="run-a",
                lap="lap-a",
                distance=[0.0, 100.0, 200.0],
                elapsed=[0.0, 10.0, 20.0],
            ),
            "lap_b": _lap_payload(
                fingerprint="sha256:lap-b",
                session="session-b",
                run="run-b",
                lap="lap-b",
                distance=[0.0, 100.0, 200.0],
                elapsed=[0.0, 11.0, 22.0],
            ),
            "grid_step_m": 100.0,
        },
        "continuous_channels": [],
        "gear": None,
    }


class _StubReportService:
    def __init__(self) -> None:
        self.request: ComparisonReportRequest | None = None

    def build(self, request: ComparisonReportRequest) -> ComparisonReportNotReady:
        self.request = request
        return ComparisonReportNotReady(
            issues=(
                ComparisonReportReadinessIssue(
                    code=ComparisonReportIssueCode.BASE_COMPARISON_NOT_READY,
                    message="stub not ready",
                ),
            )
        )


class Plan015LocalHttpApiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(create_app())

    def test_health_endpoint_contract(self) -> None:
        response = self.client.get("/healthz")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "status": "ok",
                "service": "ome-api",
                "api_version": "v1",
            },
        )

    def test_report_success_serializes_deterministic_application_artifact(self) -> None:
        response = self.client.post(
            "/api/v1/comparison-reports",
            json=_success_payload(),
        )

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["status"], "success")

        report = body["report"]
        self.assertEqual(
            report["comparison"]["distance_grid_m"],
            [0.0, 100.0, 200.0],
        )
        self.assertEqual(
            report["comparison"]["delta_b_vs_a_s"],
            [0.0, 1.0, 2.0],
        )
        self.assertEqual(
            [item["canonical_concept"] for item in report["supporting_evidence"]],
            [
                "vehicle.speed",
                "driver.throttle",
                "driver.brake",
                "driver.steering",
                "engine.speed",
                "transmission.gear",
            ],
        )
        self.assertTrue(
            all(item["status"] == "not_ready" for item in report["supporting_evidence"])
        )
        self.assertEqual(
            report["provenance"]["assembler_id"],
            "ome.lap-comparison.report",
        )
        self.assertEqual(
            report["provenance"]["base_comparison"]["algorithm_id"],
            "ome.lap-comparison.distance-linear",
        )

    def test_report_not_ready_is_a_normal_http_200_outcome(self) -> None:
        payload = _success_payload()
        comparison = payload["comparison"]
        assert isinstance(comparison, dict)
        lap_b = comparison["lap_b"]
        assert isinstance(lap_b, dict)
        lap_b["distance"] = None

        response = self.client.post(
            "/api/v1/comparison-reports",
            json=payload,
        )

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["status"], "not_ready")
        self.assertEqual(
            body["issues"][0]["code"],
            "base_comparison_not_ready",
        )
        self.assertIn(
            "missing_distance",
            [issue["code"] for issue in body["base_comparison"]["issues"]],
        )

    def test_invalid_transport_payload_returns_422(self) -> None:
        response = self.client.post(
            "/api/v1/comparison-reports",
            json={"continuous_channels": []},
        )

        self.assertEqual(response.status_code, 422)

    def test_openapi_contains_only_v0_1_product_routes(self) -> None:
        response = self.client.get("/openapi.json")

        self.assertEqual(response.status_code, 200)
        paths = response.json()["paths"]
        self.assertEqual(
            set(paths),
            {
                "/healthz",
                "/api/v1/comparison-reports",
            },
        )

    def test_transport_delegates_to_application_service(self) -> None:
        service = _StubReportService()
        client = TestClient(create_app(report_service=service))

        response = client.post(
            "/api/v1/comparison-reports",
            json=_success_payload(),
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "not_ready")
        self.assertIsInstance(service.request, ComparisonReportRequest)
        assert service.request is not None
        self.assertEqual(service.request.comparison.grid_step_m, 100.0)
        self.assertEqual(service.request.comparison.lap_a.context.lap_identifier, "lap-a")


if __name__ == "__main__":
    unittest.main()
