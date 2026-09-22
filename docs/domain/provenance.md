# Telemetry Provenance

Status: **Accepted domain foundation**

## Purpose

Provenance answers:

> Where did this data or result come from?

Provenance is part of engineering evidence, not optional bookkeeping.

## Minimum provenance for file-based imports

Every successfully imported file-based dataset must be capable of retaining:

- original source name;
- source format/type;
- source-system identity when known;
- stable content fingerprint;
- source size when available;
- importer identity;
- importer version;
- import parameters that affect meaning;
- import timestamp;
- source metadata preserved by the importer.

The implementation mechanism is intentionally not specified here.

## Channel provenance

Every imported SourceChannel must remain traceable to:

- the imported dataset;
- its original source name/identifier;
- original unit when supplied;
- source acquisition metadata when supplied.

Canonical mappings must not replace this information.

## Derived-data provenance

Every deterministic derived metric should be capable of recording:

- metric/algorithm identity;
- algorithm version;
- source channels;
- parameters;
- unit/conversion assumptions;
- output unit.

## Finding provenance

A Finding should be able to reference:

- observations;
- metrics;
- dataset/run/lap/segment context;
- source evidence;
- analysis version;
- known missing evidence.

## Duplicate-source policy

A stable source fingerprint should be used to detect identical source content within the same workspace or project context.

Default behavior:

- notify that identical source content already exists;
- reuse/reference the existing imported dataset by default;
- allow an explicit re-import when needed for importer-version or parameter comparison.

Filename alone must never be treated as sufficient proof of identity.

## Operational timestamps

Import timestamps describe OME activity.

They must not be confused with:

- source recording time;
- session time;
- channel timestamps.

These time concepts remain separate.
