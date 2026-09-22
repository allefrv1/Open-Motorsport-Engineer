from __future__ import annotations

import unittest
from datetime import UTC, datetime
from pathlib import Path

import ome.domain as domain
from ome.application.context import ContextOrganizer
from ome.domain import (
    ContextEvidence,
    ContextMarker,
    RunOperationalMetadata,
)
from ome.ingestion import ImportSuccess, OMECsvProfileImporter

ROOT = Path(__file__).resolve().parents[2]
OME_FIXTURE = ROOT / "fixtures" / "ome" / "basic-lap.csv"
FIXED_TIME = datetime(2026, 9, 22, 12, 0, tzinfo=UTC)
FINGERPRINT = "sha256:req-003-fixture"


def marker(value: str | int, source_field: str) -> ContextMarker:
    return ContextMarker(value=value, source_field=source_field)


def evidence(
    *,
    session: ContextMarker | None,
    run: ContextMarker | None = None,
    lap: ContextMarker | None = None,
    lap_number: int | None = None,
    run_metadata: RunOperationalMetadata | None = None,
) -> ContextEvidence:
    return ContextEvidence(
        dataset_fingerprint=FINGERPRINT,
        source_identity="fixture.csv",
        session_marker=session,
        run_marker=run,
        lap_marker=lap,
        lap_number=lap_number,
        run_metadata=run_metadata,
    )


class Req003SessionRunLapContextTests(unittest.TestCase):
    def setUp(self) -> None:
        self.organizer = ContextOrganizer()

    def test_ac001_known_session_run_lap_hierarchy_is_representable(self) -> None:
        source = evidence(
            session=marker("Practice 1", "context.session"),
            run=marker("Run A", "context.run"),
            lap=marker(3, "context.lap"),
            lap_number=3,
        )

        session = self.organizer.organize(source)

        self.assertIsNotNone(session)
        assert session is not None
        self.assertEqual(len(session.runs), 1)
        self.assertEqual(session.laps_without_run, ())

        run = session.runs[0]
        self.assertEqual(len(run.laps), 1)
        self.assertEqual(run.laps[0].lap_number, 3)
        self.assertEqual(run.laps[0].source_marker.value, 3)

    def test_ac002_missing_run_boundary_is_not_invented(self) -> None:
        source = evidence(
            session=marker("Practice 1", "context.session"),
            lap=marker(3, "context.lap"),
            lap_number=3,
        )

        session = self.organizer.organize(source)

        self.assertIsNotNone(session)
        assert session is not None
        self.assertEqual(session.runs, ())
        self.assertEqual(len(session.laps_without_run), 1)
        self.assertEqual(session.laps_without_run[0].lap_number, 3)

    def test_ac002_missing_lap_evidence_does_not_create_a_lap(self) -> None:
        source = evidence(
            session=marker("Practice 1", "context.session"),
            run=marker("Run A", "context.run"),
        )

        session = self.organizer.organize(source)

        self.assertIsNotNone(session)
        assert session is not None
        self.assertEqual(len(session.runs), 1)
        self.assertEqual(session.runs[0].laps, ())
        self.assertEqual(session.laps_without_run, ())

    def test_ac003_source_markers_and_dataset_provenance_are_preserved(self) -> None:
        source = evidence(
            session=marker("Qualifying", "source.metadata.context.session"),
            run=marker("Outing 2", "source.metadata.context.run"),
            lap=marker("lap-7", "source.metadata.context.lap"),
            lap_number=7,
        )

        session = self.organizer.organize(source)

        self.assertIsNotNone(session)
        assert session is not None
        run = session.runs[0]
        lap = run.laps[0]

        self.assertEqual(session.source_marker.value, "Qualifying")
        self.assertEqual(session.source_marker.source_field, "source.metadata.context.session")
        self.assertEqual(run.source_marker.value, "Outing 2")
        self.assertEqual(run.source_marker.source_field, "source.metadata.context.run")
        self.assertEqual(lap.source_marker.value, "lap-7")
        self.assertEqual(lap.source_marker.source_field, "source.metadata.context.lap")

        self.assertEqual(session.dataset_fingerprint, FINGERPRINT)
        self.assertEqual(run.dataset_fingerprint, FINGERPRINT)
        self.assertEqual(lap.dataset_fingerprint, FINGERPRINT)
        self.assertEqual(session.source_identity, "fixture.csv")
        self.assertEqual(run.source_identity, "fixture.csv")
        self.assertEqual(lap.source_identity, "fixture.csv")

    def test_ac004_run_operational_metadata_is_context_not_telemetry(self) -> None:
        metadata = RunOperationalMetadata(
            driver="Driver 01",
            vehicle="Car 07",
            setup_version="setup-v3",
            tyre_set="set-2",
            fuel_energy_state="18 L",
            run_plan="5 push laps",
            driver_feedback="Entry understeer",
            conditions="Dry, 28 C track",
        )
        source = evidence(
            session=marker("Test", "context.session"),
            run=marker("Run 4", "context.run"),
            run_metadata=metadata,
        )

        session = self.organizer.organize(source)

        self.assertIsNotNone(session)
        assert session is not None
        run = session.runs[0]
        self.assertEqual(run.operational_metadata, metadata)
        self.assertEqual(run.operational_metadata.driver, "Driver 01")
        self.assertEqual(run.operational_metadata.vehicle, "Car 07")
        self.assertEqual(run.operational_metadata.setup_version, "setup-v3")
        self.assertEqual(run.operational_metadata.tyre_set, "set-2")
        self.assertEqual(run.operational_metadata.fuel_energy_state, "18 L")
        self.assertEqual(run.operational_metadata.run_plan, "5 push laps")
        self.assertEqual(run.operational_metadata.driver_feedback, "Entry understeer")
        self.assertEqual(run.operational_metadata.conditions, "Dry, 28 C track")

    def test_ac005_stint_is_not_forced_into_the_initial_model(self) -> None:
        source = evidence(
            session=marker("Race test", "context.session"),
            run=marker("Run 1", "context.run"),
        )

        session = self.organizer.organize(source)

        self.assertIsNotNone(session)
        assert session is not None
        run = session.runs[0]
        self.assertFalse(hasattr(domain, "StintContext"))
        self.assertFalse(hasattr(run, "stint"))

    def test_context_identifiers_are_deterministic_for_same_explicit_evidence(self) -> None:
        source = evidence(
            session=marker("Practice 1", "context.session"),
            run=marker("Run A", "context.run"),
            lap=marker(3, "context.lap"),
            lap_number=3,
        )

        first = self.organizer.organize(source)
        second = self.organizer.organize(source)

        self.assertEqual(first, second)
        assert first is not None
        self.assertEqual(first.identifier, second.identifier)
        self.assertEqual(first.runs[0].identifier, second.runs[0].identifier)
        self.assertEqual(first.runs[0].laps[0].identifier, second.runs[0].laps[0].identifier)

    def test_run_without_session_is_rejected_instead_of_attached_silently(self) -> None:
        source = evidence(
            session=None,
            run=marker("Run A", "context.run"),
        )

        with self.assertRaisesRegex(ValueError, "session"):
            self.organizer.organize(source)

    def test_lap_without_session_is_rejected_instead_of_attached_silently(self) -> None:
        source = evidence(
            session=None,
            lap=marker(1, "context.lap"),
            lap_number=1,
        )

        with self.assertRaisesRegex(ValueError, "session"):
            self.organizer.organize(source)

    def test_ome_fixture_context_is_preserved_without_inventing_a_run(self) -> None:
        outcome = OMECsvProfileImporter().import_source(
            OME_FIXTURE,
            imported_at=FIXED_TIME,
        )
        self.assertIsInstance(outcome, ImportSuccess)
        assert isinstance(outcome, ImportSuccess)

        dataset = outcome.dataset
        raw_context = dataset.source.metadata["context"]
        self.assertIsInstance(raw_context, dict | type(dataset.source.metadata))
        session_value = raw_context["session"]
        lap_value = raw_context["lap"]

        source = ContextEvidence(
            dataset_fingerprint=dataset.provenance.content_fingerprint,
            source_identity=dataset.source.original_name,
            session_marker=ContextMarker(
                value=str(session_value),
                source_field="source.metadata.context.session",
            ),
            lap_marker=ContextMarker(
                value=int(lap_value),
                source_field="source.metadata.context.lap",
            ),
            lap_number=int(lap_value),
        )

        session = self.organizer.organize(source)

        self.assertIsNotNone(session)
        assert session is not None
        self.assertEqual(session.source_marker.value, "Harness fixture")
        self.assertEqual(session.runs, ())
        self.assertEqual(len(session.laps_without_run), 1)
        self.assertEqual(session.laps_without_run[0].lap_number, 1)


if __name__ == "__main__":
    unittest.main()
