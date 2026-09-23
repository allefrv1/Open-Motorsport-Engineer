from __future__ import annotations

from typing import Protocol

from fastapi import FastAPI

from ome.application import (
    ComparisonReportOutcome,
    ComparisonReportService,
    ComparisonReportSuccess,
)
from ome.api.models import (
    ComparisonReportHttpResponse,
    ComparisonReportNotReadyResponse,
    ComparisonReportRequestDto,
    ComparisonReportSuccessDto,
    ComparisonReportSuccessResponse,
    HealthResponse,
)


class ReportBuilder(Protocol):
    def build(self, request: object) -> ComparisonReportOutcome: ...


def create_app(
    report_service: ReportBuilder | None = None,
) -> FastAPI:
    service = report_service if report_service is not None else ComparisonReportService()

    app = FastAPI(
        title="Open Motorsport Engineer API",
        version="0.1.0",
    )

    @app.get("/healthz", response_model=HealthResponse)
    def healthz() -> HealthResponse:
        return HealthResponse()

    @app.post(
        "/api/v1/comparison-reports",
        response_model=ComparisonReportHttpResponse,
    )
    def comparison_report(
        payload: ComparisonReportRequestDto,
    ) -> ComparisonReportHttpResponse:
        outcome = service.build(payload.to_domain())
        if isinstance(outcome, ComparisonReportSuccess):
            return ComparisonReportSuccessResponse(
                report=ComparisonReportSuccessDto.from_domain(outcome)
            )
        return ComparisonReportNotReadyResponse.from_domain(outcome)

    return app
