from __future__ import annotations

from dataclasses import dataclass

ContextMarkerValue = str | int


@dataclass(frozen=True, slots=True)
class ContextMarker:
    value: ContextMarkerValue
    source_field: str

    def __post_init__(self) -> None:
        if not self.source_field.strip():
            raise ValueError("context marker source_field must be non-empty")


@dataclass(frozen=True, slots=True)
class RunOperationalMetadata:
    driver: str | None = None
    vehicle: str | None = None
    setup_version: str | None = None
    tyre_set: str | None = None
    fuel_energy_state: str | None = None
    run_plan: str | None = None
    driver_feedback: str | None = None
    conditions: str | None = None


@dataclass(frozen=True, slots=True)
class ContextEvidence:
    dataset_fingerprint: str
    source_identity: str
    session_marker: ContextMarker | None = None
    run_marker: ContextMarker | None = None
    lap_marker: ContextMarker | None = None
    lap_number: int | None = None
    lap_start_s: float | None = None
    lap_end_s: float | None = None
    run_metadata: RunOperationalMetadata | None = None

    def __post_init__(self) -> None:
        if not self.dataset_fingerprint.strip():
            raise ValueError("dataset_fingerprint must be non-empty")
        if not self.source_identity.strip():
            raise ValueError("source_identity must be non-empty")


@dataclass(frozen=True, slots=True)
class LapContext:
    identifier: str
    dataset_fingerprint: str
    source_identity: str
    source_marker: ContextMarker
    lap_number: int | None = None
    start_s: float | None = None
    end_s: float | None = None


@dataclass(frozen=True, slots=True)
class RunContext:
    identifier: str
    dataset_fingerprint: str
    source_identity: str
    source_marker: ContextMarker
    laps: tuple[LapContext, ...]
    operational_metadata: RunOperationalMetadata


@dataclass(frozen=True, slots=True)
class SessionContext:
    identifier: str
    dataset_fingerprint: str
    source_identity: str
    source_marker: ContextMarker
    runs: tuple[RunContext, ...]
    laps_without_run: tuple[LapContext, ...]
