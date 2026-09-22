# ADR-0002 — CSV is an exchange profile, not OME's canonical telemetry storage

Status: **Accepted**

Date: 2026-09-22

## Context

OME needs a simple open format for fixtures, examples and basic interchange.

CSV is useful because it is human-readable and supported broadly by analysis tools.

However, real telemetry may contain:

- independent sample rates;
- different time bases;
- rich channel metadata;
- source-specific calibration/conversion information;
- events;
- gaps;
- attachments;
- non-tabular information.

Using one flat CSV table as the canonical internal model would encourage hidden resampling and loss of metadata.

## Decision

OME CSV Exchange Profile is accepted for:

- deterministic fixtures;
- examples;
- simple interchange;
- early vertical-slice validation.

It is **not** the canonical internal telemetry model.

The internal representation must be selected later against the Telemetry Import Model and quality attributes.

## Consequences

### Positive

- fixtures remain simple and inspectable;
- source adapters are free to represent richer telemetry faithfully;
- CSV limitations do not dictate OME's domain model;
- future MDF/MF4 or vendor adapters remain feasible.

### Negative

- the project will eventually need a richer internal representation;
- conversion to/from CSV may be lossy for multi-rate datasets;
- users must be warned when exporting richer data to a flat profile.

## Alternatives considered

### CSV as internal canonical format

Rejected because it does not naturally preserve multi-rate measurement semantics and rich provenance.

### Adopt a professional binary format immediately

Deferred because selecting an internal persistence/storage format before implementation benchmarks would be premature.

## Related artifacts

- `docs/specs/ome-csv-profile-v0.1.md`
- `docs/domain/telemetry-import-model.md`
- `docs/QUALITY_ATTRIBUTES.md`
