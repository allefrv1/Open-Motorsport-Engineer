# Third-Party Fixture Notices

## exit_speed — Traqmate parking-lot telemetry

OME path:

`fixtures/public/exit-speed/traqmate-parking-lot.csv`

Upstream repository:

https://github.com/djhedges/exit_speed

Upstream path:

`exit_speed/testdata/test_parking_lot_20hz_2020-06-11T22_1.csv`

Upstream Git blob SHA at verification:

`df9aaa9827b85d33c4df4d5dd11912955e2240cf`

License:

Apache License 2.0.

The upstream license text is retained at:

`fixtures/public/licenses/exit-speed-Apache-2.0.txt`

Use in OME:

Testing and validating generic telemetry ingestion concepts such as metadata preamble, elapsed time, GPS, velocity and lap context.

## exit_speed — Portland Traqmate laps 4–5 derived slice

OME path:

`fixtures/public/exit-speed/traqmate-portland-laps-4-5.csv`

Upstream repository:

https://github.com/djhedges/exit_speed

Upstream path:

`exit_speed/testdata/2019-08-18_Portland_CORRADO_DJ_R03_stripped.csv`

Upstream Git blob SHA at verification:

`499762a9044ea0b09a698509e84681877baf7897`

Derived slice:

- original preamble and telemetry header preserved;
- zero-based upstream data rows 11,360 through 18,609 inclusive;
- 7,250 source data rows;
- source cells are not rewritten;
- sparse source Lap markers 4, 5 and boundary marker 6 are preserved.

License:

Apache License 2.0.

The upstream license text is retained at:

`fixtures/public/licenses/exit-speed-Apache-2.0.txt`

Use in OME:

Testing the real extended Trackvision V2 layout and preserving two complete physical-car Portland laps for later comparison preparation.

## TRACE — MoTeC CSV canonical fixture

OME path:

`fixtures/public/trace/motec-canonical.csv`

Upstream repository:

https://github.com/keystroke-tools/TRACE

Upstream path:

`crates/trace-motec/tests/fixtures/csv/canonical.csv`

Upstream Git blob SHA at verification:

`50f23127dff0b880d768ea91aa309bdc99f14432`

License:

MIT.

The upstream license text is retained at:

`fixtures/public/licenses/trace-MIT.txt`

Use in OME:

Testing MoTeC-style CSV structure and source-preserving import behavior.

## TRACE — decreasing-time fixture

OME path:

`fixtures/public/trace/motec-decreasing-time.csv`

Upstream repository:

https://github.com/keystroke-tools/TRACE

Upstream path:

`crates/trace-motec/tests/fixtures/csv/decreasing-time.csv`

License:

MIT.

Use in OME:

Negative validation case for non-monotonic/decreasing time.
