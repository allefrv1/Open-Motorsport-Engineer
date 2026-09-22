from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class ValidationSeverity(StrEnum):
    BLOCKING = "blocking"
    WARNING = "warning"
    INFO = "info"


class ValidationCategory(StrEnum):
    STRUCTURE = "structure"
    TIME = "time"
    METADATA = "metadata"
    VALUES = "values"
    SYNCHRONIZATION = "synchronization"


class ValidationIssueCode(StrEnum):
    EMPTY_SAMPLE_SERIES = "empty_sample_series"
    NON_FINITE_TIMESTAMP = "non_finite_timestamp"
    DUPLICATE_TIMESTAMP = "duplicate_timestamp"
    DECREASING_TIMESTAMP = "decreasing_timestamp"
    MISSING_CHANNEL_UNIT = "missing_channel_unit"
    MISSING_SAMPLE_RATE = "missing_sample_rate"
    INVALID_SAMPLE_RATE = "invalid_sample_rate"
    MISSING_SOURCE_IDENTITY = "missing_source_identity"


@dataclass(frozen=True, slots=True)
class ValidationLocation:
    channel_identifier: str | None = None
    sample_index: int | None = None
    timestamp_s: float | None = None
    field: str | None = None


@dataclass(frozen=True, slots=True)
class ValidationIssue:
    code: ValidationIssueCode
    category: ValidationCategory
    severity: ValidationSeverity
    message: str
    location: ValidationLocation


@dataclass(frozen=True, slots=True)
class ValidationResult:
    dataset_fingerprint: str
    issues: tuple[ValidationIssue, ...]

    @property
    def has_blocking_issues(self) -> bool:
        return any(issue.severity is ValidationSeverity.BLOCKING for issue in self.issues)

    @property
    def blocking_issues(self) -> tuple[ValidationIssue, ...]:
        return tuple(
            issue for issue in self.issues if issue.severity is ValidationSeverity.BLOCKING
        )
