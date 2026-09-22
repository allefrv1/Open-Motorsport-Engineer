# Telemetry Data Quality

Status: **Accepted domain foundation**

## Principle

Readable data is not automatically trustworthy data.

OME must distinguish successful ingestion from data-quality validation.

## Validation dimensions

The initial validation model should be capable of checking:

### Structure

- unreadable or malformed structures;
- missing required source sections;
- inconsistent sample counts where the source contract requires consistency.

### Time

- missing time basis;
- non-monotonic time where monotonicity is required;
- duplicate timestamps;
- time gaps;
- suspicious discontinuities.

### Values

- NaN / non-finite values;
- frozen signals;
- clipping/saturation;
- impossible or suspicious ranges;
- abrupt spikes.

Range checks must be channel-aware and must not invent universal physical limits without validated rules.

### Metadata

- missing units;
- unknown sample rates;
- absent source identity;
- ambiguous channel identity;
- unsupported conversions.

### Synchronization

- mismatched time bases;
- known synchronization gaps;
- inconsistent start/end ranges.

## Severity

Validation issues should use at least:

- **BLOCKING** — dataset cannot safely proceed for the affected operation;
- **WARNING** — analysis may proceed with visible limitation;
- **INFO** — noteworthy but not inherently problematic.

## No silent repair

Validation reports problems.

It must not silently:

- interpolate missing values;
- change units;
- rename channels;
- remove spikes;
- fill gaps;
- resample signals.

Those are explicit transformations and require separate rules.

## Analysis-specific readiness

A dataset is not globally "valid for everything."

Readiness should be evaluated against an intended analysis.

Examples:

- RPM analysis may be possible without GPS;
- yaw-response analysis is not possible without appropriate directional-response evidence;
- lap comparison needs a trustworthy comparison reference.

Therefore:

```text
VALIDATED DATASET
+ ANALYSIS REQUIREMENTS
= ANALYSIS READINESS
```

## First-version corruption policy

For structural corruption that prevents trustworthy interpretation of the source:

- fail the import or validation explicitly;
- do not expose the dataset as usable.

The first version will not attempt partial recovery of structurally corrupted telemetry.

Missing non-critical metadata may produce warnings rather than total failure.
