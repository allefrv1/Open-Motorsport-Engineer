# OME First Vertical Slice

Status: **Accepted product/engineering scope**

## Objective

Validate OME's core value proposition without attempting to build a complete motorsport analysis platform.

The first vertical slice must demonstrate that OME can move from a real telemetry source to a reproducible engineering comparison while preserving evidence.

## User story

A user should be able to:

1. import a supported telemetry dataset;
2. understand what channels and metadata are available;
3. see whether the dataset has blocking quality problems;
4. organize or use known Session / Run / Lap context;
5. select two laps;
6. compare key driver/performance channels;
7. locate where time was gained or lost;
8. inspect the evidence behind that difference.

## Initial source scope

Required for the first implementation sequence:

1. **OME CSV Exchange Profile** — controlled fixtures and simple interchange;
2. **iRacing .ibt** — first external binary adapter;
3. **MoTeC CSV export** — first real-motorsport professional workflow path.

Native MoTeC `.ld` support is explicitly deferred from the first vertical slice.

## Initial analysis scope

The first comparison should focus on channels commonly useful for lap analysis when available:

- time;
- lap distance or equivalent positional reference;
- vehicle speed;
- throttle;
- brake;
- steering;
- RPM;
- gear.

Not every source must contain every channel.

Missing channels must be reported, not synthesized.

## Required capabilities

### Import

Source data becomes an ImportedTelemetryDataset with provenance.

### Inventory

The user can inspect original channel names, units and acquisition metadata when present.

### Validation

Blocking structural problems and important warnings are reported before analysis.

### Organization

The system can represent Session / Run / Lap context.

For the first slice, lap boundaries may come from trusted source metadata or explicit fixture metadata. Automatic generic lap detection is not required.

### Comparison

Two laps can be aligned on an explicit comparison reference.

The exact alignment algorithm must be specified before implementation.

### Evidence

A comparison result must distinguish measured values, derived metrics and observations.

### Preparation workflow

Plan 016 adds the application-level bridge from imported source evidence to the accepted comparison/report stack.

For the controlled first path:

```text
OME CSV source
-> ImportedTelemetryDataset
-> validation
-> explicit versioned normalization profile
-> explicit Session / Run / Lap context
-> canonical distance/time/supporting evidence
-> ComparisonReportRequest
-> ComparisonReportService
```

Executable coverage:

`tests/application/test_comparison_preparation.py`

The workflow does not perform generic lap detection, fuzzy channel matching or source repair.

It returns explicit not-ready/Missing Evidence when trustworthy preparation is impossible.

## Explicitly out of scope

- live telemetry;
- race strategy;
- automatic setup recommendations;
- user-facing tyre-analysis workflows and vehicle-level tyre simulation;\n- an isolated deterministic tyre-model foundation may be added only through an explicit requirement/ADR and does not become part of the MVP comparison flow;
- advanced damper analysis;
- aerodynamics models;
- complete vehicle simulation;
- generic AI chat over raw data;
- cloud collaboration;
- automatic support for arbitrary CSV layouts;
- native MoTeC `.ld` as a requirement;
- automatic diagnosis of understeer/oversteer.

## Success criterion

The first vertical slice is successful when a user can take a representative dataset and answer:

> Where did Lap B gain or lose time relative to Lap A, and which measured evidence supports that observation?

without OME inventing missing data or hiding transformations.
