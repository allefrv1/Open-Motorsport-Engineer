# Public Telemetry Fixtures

This directory contains small third-party telemetry fixtures that OME is permitted to redistribute and use for deterministic testing.

## Included

### exit-speed / Traqmate parking-lot telemetry

Path:

`exit-speed/traqmate-parking-lot.csv`

Purpose:

- real vehicle telemetry shape;
- metadata preamble;
- GPS coordinates;
- velocity;
- explicit lap number;
- fixed 10 Hz time base.

Source project:

https://github.com/djhedges/exit_speed

License:

Apache License 2.0. See `licenses/exit-speed-Apache-2.0.txt`.

### exit-speed / Portland Traqmate laps 4–5

Path:

`exit-speed/traqmate-portland-laps-4-5.csv`

Purpose:

- real Portland physical-car telemetry;
- extended 28-column Trackvision V2 layout;
- 40 Hz source cadence;
- sparse Lap boundary markers;
- complete source Laps 4 and 5.

This is a contiguous derived slice of upstream blob
`499762a9044ea0b09a698509e84681877baf7897`.
The original preamble/header and selected source cells are preserved.

License:

Apache License 2.0. See `licenses/exit-speed-Apache-2.0.txt`.

### TRACE / MoTeC CSV fixtures

Paths:

- `trace/motec-canonical.csv`
- `trace/motec-decreasing-time.csv`

Purpose:

- MoTeC-style CSV metadata/channel/unit layout;
- mixed numeric/discrete/missing-like values;
- validation case with decreasing time.

Source project:

https://github.com/keystroke-tools/TRACE

License:

MIT. See `licenses/trace-MIT.txt`.

## Not vendored here

Some public telemetry sources are intentionally **not copied** into OME even though they are useful for validation.

Reasons can include:

- no explicit redistribution license;
- vendor/simulator-generated data with unclear redistribution rights;
- large files better kept as external benchmark data.

See:

- `docs/research/public-telemetry-datasets.md`
- `fixtures/public/manifest.json`
- `THIRD_PARTY_NOTICES.md`

## Rule

Publicly accessible does not automatically mean redistributable.

A fixture must have an explicit provenance and redistribution decision before it is committed here.
