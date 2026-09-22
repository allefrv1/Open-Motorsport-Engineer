from __future__ import annotations

from collections.abc import Callable, Iterable

from ome.domain import ImportedTelemetryDataset, ValidationIssue, ValidationResult
from ome.validation.checks import check_metadata, check_time_structure, check_values

ValidationCheck = Callable[[ImportedTelemetryDataset], tuple[ValidationIssue, ...]]


class TelemetryValidator:
    validator_id = "ome.telemetry-validator"
    validator_version = "0.1.0"

    def __init__(self, checks: Iterable[ValidationCheck] | None = None) -> None:
        self._checks = tuple(
            checks if checks is not None else (check_time_structure, check_metadata, check_values)
        )

    def validate(self, dataset: ImportedTelemetryDataset) -> ValidationResult:
        issues = tuple(issue for check in self._checks for issue in check(dataset))
        return ValidationResult(
            dataset_fingerprint=dataset.provenance.content_fingerprint,
            validator_id=self.validator_id,
            validator_version=self.validator_version,
            issues=issues,
        )
