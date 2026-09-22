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
