# Ingestion module instructions

These rules apply to `backend/src/ome/ingestion/`.

## Responsibility

Ingestion answers:

> What did the source contain, and where did it come from?

## Required behavior

- Preserve source channel identity, units and metadata.
- Preserve provenance and a stable content fingerprint.
- Return explicit failures instead of valid-looking partial datasets.
- Represent missing metadata explicitly.
- Keep importer behavior deterministic apart from operational metadata such as import time.
- Implement source adapters behind the common ingestion contract.

## Forbidden behavior

Do not:

- normalize source channels into canonical engineering concepts;
- convert units silently;
- resample/interpolate signals;
- repair missing or suspicious telemetry;
- infer Session / Run / Lap boundaries generically;
- make engineering diagnoses;
- introduce API/UI concerns into adapters.

Format-contract checks needed to safely parse a source are allowed.

Data-quality analysis belongs to the validation layer.
