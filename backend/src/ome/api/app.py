from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Annotated, Protocol

from fastapi import FastAPI, File, Form, UploadFile

from ome.api.models import (
    ComparisonReportHttpResponse,
    ComparisonReportNotReadyResponse,
    ComparisonReportRequestDto,
    ComparisonReportSuccessDto,
    ComparisonReportSuccessResponse,
    HealthResponse,
    OmeCsvComparisonHttpResponse,
    OmeCsvComparisonNotReadyResponse,
    WorkflowIssueDto,
)
from ome.api.upload_workflow import stage_ome_csv_bundle
from ome.application import (
    ComparisonPreparationNotReady,
    ComparisonPreparationRequest,
    ComparisonPreparationService,
    ComparisonPreparationSuccess,
    ComparisonReportNotReady,
    ComparisonReportOutcome,
    ComparisonReportRequest,
    ComparisonReportService,
    ComparisonReportSuccess,
    mvp_ome_csv_comparison_profile,
)
from ome.ingestion import ImportFailure, ImportSuccess, OMECsvProfileImporter


class ReportBuilder(Protocol):
    def build(self, request: ComparisonReportRequest) -> ComparisonReportOutcome: ...


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

    importer = OMECsvProfileImporter()
    preparation_service = ComparisonPreparationService()
    preparation_profile = mvp_ome_csv_comparison_profile()

    @app.post(
        "/api/v1/ome-csv/comparison-reports",
        response_model=OmeCsvComparisonHttpResponse,
    )
    def ome_csv_comparison_report(
        lap_a_csv: Annotated[UploadFile, File()],
        lap_a_sidecar: Annotated[UploadFile, File()],
        lap_b_csv: Annotated[UploadFile, File()],
        lap_b_sidecar: Annotated[UploadFile, File()],
        grid_step_m: Annotated[float, Form()] = 1.0,
    ) -> OmeCsvComparisonHttpResponse:
        with TemporaryDirectory(prefix="ome-api-upload-") as temporary:
            root = Path(temporary)
            lap_a_path = stage_ome_csv_bundle(
                root,
                lap_side="a",
                csv_upload=lap_a_csv,
                sidecar_upload=lap_a_sidecar,
            )
            lap_b_path = stage_ome_csv_bundle(
                root,
                lap_side="b",
                csv_upload=lap_b_csv,
                sidecar_upload=lap_b_sidecar,
            )

            lap_a_import = importer.import_source(lap_a_path)
            if isinstance(lap_a_import, ImportFailure):
                return OmeCsvComparisonNotReadyResponse(
                    stage="import",
                    issues=(
                        WorkflowIssueDto.from_import_failure(
                            lap_a_import,
                            lap_side="a",
                        ),
                    ),
                )
            assert isinstance(lap_a_import, ImportSuccess)

            lap_b_import = importer.import_source(lap_b_path)
            if isinstance(lap_b_import, ImportFailure):
                return OmeCsvComparisonNotReadyResponse(
                    stage="import",
                    issues=(
                        WorkflowIssueDto.from_import_failure(
                            lap_b_import,
                            lap_side="b",
                        ),
                    ),
                )
            assert isinstance(lap_b_import, ImportSuccess)

            preparation = preparation_service.prepare(
                ComparisonPreparationRequest(
                    lap_a=lap_a_import.dataset,
                    lap_b=lap_b_import.dataset,
                    profile=preparation_profile,
                    grid_step_m=grid_step_m,
                )
            )
            if isinstance(preparation, ComparisonPreparationNotReady):
                return OmeCsvComparisonNotReadyResponse(
                    stage="preparation",
                    issues=tuple(
                        WorkflowIssueDto.from_preparation_issue(issue)
                        for issue in preparation.issues
                    ),
                )
            assert isinstance(preparation, ComparisonPreparationSuccess)

            report = service.build(preparation.report_request)
            if isinstance(report, ComparisonReportNotReady):
                return OmeCsvComparisonNotReadyResponse(
                    stage="report",
                    issues=tuple(
                        WorkflowIssueDto.from_report_issue(issue) for issue in report.issues
                    ),
                )

            assert isinstance(report, ComparisonReportSuccess)
            return ComparisonReportSuccessResponse(
                report=ComparisonReportSuccessDto.from_domain(report)
            )

    return app
