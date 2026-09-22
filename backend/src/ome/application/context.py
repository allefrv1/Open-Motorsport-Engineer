from __future__ import annotations

import hashlib

from ome.domain import (
    ContextEvidence,
    ContextMarker,
    LapContext,
    RunContext,
    RunOperationalMetadata,
    SessionContext,
)


class ContextOrganizer:
    """Organize only explicit trusted operational context evidence."""

    def organize(self, evidence: ContextEvidence) -> SessionContext | None:
        self._check_consistency(evidence)

        session_marker = evidence.session_marker
        if session_marker is None:
            return None

        lap = self._lap_context(evidence)
        run = self._run_context(evidence, lap)

        return SessionContext(
            identifier=self._identifier(
                "session",
                evidence,
                session_marker,
            ),
            dataset_fingerprint=evidence.dataset_fingerprint,
            source_identity=evidence.source_identity,
            source_marker=session_marker,
            runs=() if run is None else (run,),
            laps_without_run=() if lap is None or run is not None else (lap,),
        )

    def _run_context(
        self,
        evidence: ContextEvidence,
        lap: LapContext | None,
    ) -> RunContext | None:
        run_marker = evidence.run_marker
        if run_marker is None:
            return None

        return RunContext(
            identifier=self._identifier(
                "run",
                evidence,
                run_marker,
                parent_marker=evidence.session_marker,
            ),
            dataset_fingerprint=evidence.dataset_fingerprint,
            source_identity=evidence.source_identity,
            source_marker=run_marker,
            laps=() if lap is None else (lap,),
            operational_metadata=evidence.run_metadata or RunOperationalMetadata(),
        )

    def _lap_context(self, evidence: ContextEvidence) -> LapContext | None:
        lap_marker = evidence.lap_marker
        if lap_marker is None:
            return None

        parent_marker = evidence.run_marker or evidence.session_marker
        return LapContext(
            identifier=self._identifier(
                "lap",
                evidence,
                lap_marker,
                parent_marker=parent_marker,
            ),
            dataset_fingerprint=evidence.dataset_fingerprint,
            source_identity=evidence.source_identity,
            source_marker=lap_marker,
            lap_number=evidence.lap_number,
            start_s=evidence.lap_start_s,
            end_s=evidence.lap_end_s,
        )

    @staticmethod
    def _check_consistency(evidence: ContextEvidence) -> None:
        has_child_context = (
            evidence.run_marker is not None
            or evidence.lap_marker is not None
            or evidence.run_metadata is not None
        )
        if evidence.session_marker is None and has_child_context:
            raise ValueError("session context is required before run or lap context")

        if evidence.run_metadata is not None and evidence.run_marker is None:
            raise ValueError("run metadata requires an explicit run marker")

        if evidence.lap_number is not None and evidence.lap_marker is None:
            raise ValueError("lap number requires an explicit lap marker")

        if (
            evidence.lap_start_s is not None or evidence.lap_end_s is not None
        ) and evidence.lap_marker is None:
            raise ValueError("lap boundaries require an explicit lap marker")

        if (
            evidence.lap_start_s is not None
            and evidence.lap_end_s is not None
            and evidence.lap_end_s < evidence.lap_start_s
        ):
            raise ValueError("lap end must not precede lap start")

    @staticmethod
    def _identifier(
        kind: str,
        evidence: ContextEvidence,
        marker: ContextMarker,
        *,
        parent_marker: ContextMarker | None = None,
    ) -> str:
        parent = ""
        if parent_marker is not None:
            parent = f"{parent_marker.source_field}={parent_marker.value}"

        payload = "\0".join(
            (
                kind,
                evidence.dataset_fingerprint,
                evidence.source_identity,
                parent,
                marker.source_field,
                str(marker.value),
            )
        )
        digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()
        return f"{kind}:{digest}"
