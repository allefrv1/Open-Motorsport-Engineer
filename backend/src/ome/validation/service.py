from __future__ import annotations

from ome.domain import ImportedTelemetryDataset, ValidationResult
from ome.validation.checks import check_metadata, check_time_structure, check_values


class TelemetryValidator:
    validator_id = "ome.telemetry-validator"
    validator_version = "0.1.0"

    def validate(self, dataset: ImportedTelemetryDataset) -> ValidationResult:
        issues = (
            *check_time_structure(dataset),
            *check_metadata(dataset),
            *check_values(dataset),
        )
        return ValidationResult(
            dataset_fingerprint=dataset.provenance.content_fingerprint,
            validator_id=self.validator_id,
            validator_version=self.validator_version,
            issues=issues,
        )
