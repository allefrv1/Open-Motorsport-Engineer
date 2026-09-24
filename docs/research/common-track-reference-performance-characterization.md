# Common Track Reference Performance Characterization

Status: **Reviewed research**

Date: 2026-09-24

## Purpose

Characterize the current direct-search implementation of:

`ome.track-reference.explicit-lap-projection/0.1.0`

without turning machine-dependent timing into a correctness gate.

This document records observed performance.

It does not define an accepted latency requirement.

## Method

The canonical GitHub Actions runner executed the production `CommonTrackReferenceEngine` against deterministic synthetic closed reference/candidate laps.

For each sample count `N`:

- the reference contained `N - 1` segments;
- the candidate contained `N` points;
- nearest-segment projection used the production direct search;
- reference self-intersection checks also used the current production implementation;
- correctness still had to pass;
- elapsed wall time was printed for characterization only.

No assertion depends on wall-clock time.

Test:

`tests/analysis/test_common_track_reference_performance.py`

CI evidence:

`OME CI #297`

## Observed result

| Samples | Candidate × reference segment checks | Observed elapsed |
|---:|---:|---:|
| 100 | 9,900 | 0.026009 s |
| 200 | 39,800 | 0.082985 s |
| 400 | 159,600 | 0.303566 s |
| 800 | 639,200 | 1.146886 s |

The observed cost per listed projection segment check trends toward roughly 1.8–2.6 microseconds on this runner.

The full elapsed value also includes:

- WGS84 local-coordinate conversion;
- reference self-intersection analysis;
- object/result construction;
- Python test overhead.

## Scaling interpretation

The current search strategy is quadratic in the common case:

```text
candidate_samples * reference_segments
```

Doubling the sample count approximately quadruples the direct projection search work.

This is acceptable as a correctness-first baseline and makes the numerical contract easy to audit.

It is not evidence that the current search strategy is suitable for every full-resolution multi-lap workload.

## Portland relationship

The reviewed Portland physical-car research already records the geometry/readiness behavior of the proposed reference projection across its multi-lap source:

- 15/16 non-reference clean laps pass strict monotonic readiness after seam unwrap;
- one lap exposes small local backtracking and remains not-ready under v0.1;
- projection vs global scaling differs materially at local positions.

The external Portland CSV is approximately 20 MB and is intentionally not vendored into OME.

During this implementation session, the GitHub content connector could identify the exact source/blob but did not return the large file body, so the new production implementation was **not** re-benchmarked against that exact external blob.

No runtime result for the Portland blob is claimed here.

## Decision

Do not introduce a spatial-index dependency solely because the direct algorithm is O(N^2).

Before acceleration work is accepted, define at least one representative performance target such as:

- maximum preparation latency per lap;
- target sample count;
- number of laps per comparison batch;
- target local hardware class.

Any acceleration must remain behind the same accepted numerical contract and prove equivalent projection/tie/readiness behavior.

## Known optimization candidates

Future work may evaluate:

- exact spatial bounding-volume indexing;
- a proven spatial-index library;
- deterministic segment candidate pruning.

Optimization must not:

- change nearest-segment semantics;
- change lowest-index tie behavior;
- smooth candidate paths;
- hide self-intersections;
- weaken provenance;
- introduce approximate nearest-neighbor behavior without a separate accepted algorithm/version.

## Conclusion

Plan 023 now has measured performance evidence for the supported direct-search path.

Correctness is green.

Scalability beyond the measured range remains an explicit optimization concern rather than a hidden assumption.
