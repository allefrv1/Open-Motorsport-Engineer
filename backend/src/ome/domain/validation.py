from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from enum import StrEnum

from ome.domain.telemetry import freeze_metadata


class ValidationSeverity(StrEnum):
    BLOCKING = "blocking"
    WARNING = "warning"
    INFO = "info"


class ValidationCategory(StrEnum):
    STRUCTURE = "structure"
    TIME = "time"
    VALUE = "value"
    METADATA = "metadata"
    SYNCHRONIZATION = "synchronization"


def _empty_evidence() -> Mapping[str, object]:
    return freeze_metadata({})


@dataclass(frozen=True, slots=True)
class ValidationIssue:
    code: str
    category: ValidationCategory
    severity: ValidationSeverity
    message: str
    channel_identifier: str | None = None
    time_start_s: float | None = None
    time_end_s: float | None = None
    evidence: Mapping[str, object] = field(default_factory=_empty_evidence)

    def __post_init__(self) -> None:
        object.__setattr__(self, "evidence", freeze_metadata(self.evidence))


@dataclass(frozen=True, slots=True)
class ValidationResult:
    dataset_fingerprint: str
    validator_id: str
    validator_version: str
    issues: tuple[ValidationIssue, ...]

    @property
    def blocking_issues(self) -> tuple[ValidationIssue, ...]:
        return tuple(
            issue for issue in self.issues if issue.severity is ValidationSeverity.BLOCKING
        )

    @property
    def warning_issues(self) -> tuple[ValidationIssue, ...]:
        return tuple(issue for issue in self.issues if issue.severity is ValidationSeverity.WARNING)

    @property
    def has_blocking_issues(self) -> bool:
        return bool(self.blocking_issues)

    def relevant_issues(self, channel_identifiers: Iterable[str]) -> tuple[ValidationIssue, ...]:
        selected = frozenset(channel_identifiers)
        return tuple(
            issue
            for issue in self.issues
            if issue.channel_identifier is None or issue.channel_identifier in selected
        )
