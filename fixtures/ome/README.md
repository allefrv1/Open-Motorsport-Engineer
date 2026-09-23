# OME-owned CSV fixtures

These fixtures are project-owned, synthetic and intentionally small.

They validate the OME CSV Exchange Profile without depending on a vendor format.

## basic-lap

Files:

- `basic-lap.csv`
- `basic-lap.ome.json`

Purpose:

- monotonic shared time base;
- channel/sidecar agreement;
- source-name and unit metadata;
- deterministic harness input.

The values are synthetic and must not be described as measured motorsport data.


Normalization fixture note:

- channels declaring `%` use percentage-point source values such as `40` for 40%;
- normalized fraction conversion is therefore explicit and testable;
- source values remain unchanged after normalization.


## mvp-comparison-lap-a / mvp-comparison-lap-b

Files:

- `mvp-comparison-lap-a.csv`
- `mvp-comparison-lap-a.ome.json`
- `mvp-comparison-lap-b.csv`
- `mvp-comparison-lap-b.ome.json`

Purpose:

- controlled Plan 016 end-to-end preparation input;
- explicit `time_s` source axis;
- explicit lap distance in metres;
- speed/throttle/brake/steering/RPM/gear evidence;
- explicit Session / Run / Lap source context;
- deterministic known delta-time case.

Both fixtures are project-owned synthetic telemetry. They are not measured motorsport data.
