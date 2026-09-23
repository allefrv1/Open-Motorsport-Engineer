# OME Interface Principles

## Product intent

OME helps users understand motorsport engineering evidence. The interface should shorten the path from an engineering question to a verifiable answer.

## Primary investigation flow

```text
Import
-> Validate
-> Contextualize
-> Compare
-> Observe
-> Investigate
-> Explain
-> Document
```

Navigation and screen organization should reinforce this flow where practical.

## Progressive disclosure

One evidence model, multiple depths:

- beginner: concise explanation and key comparison;
- intermediate: relevant metrics, context, overlays and warnings;
- engineer: source channels, derived channels, methods, units, provenance and detailed plots.

Do not hide the source evidence from expert users or expose every raw channel to beginners by default.

## Evidence distinction

Never visually present these as equivalent:

- measured telemetry;
- deterministic derived metric;
- observation;
- hypothesis;
- engineering interpretation;
- possible action;
- AI explanation.

Use labels, grouping, metadata, icons, typography, or other redundant cues. Do not rely on color alone.

## Comparison UX

For two-lap comparison, always make discoverable:

- Lap A and Lap B identity/context;
- which one is the reference;
- delta sign convention;
- distance/alignment basis;
- comparable interval;
- units;
- missing channels/evidence;
- algorithm/version or method details when the user opens provenance.

The UI must not imply causal diagnosis from correlation.

## Telemetry visualization

- Synchronize plots on the explicit comparison reference.
- Preserve exact values through hover/inspection or a data cursor.
- Use shared cursor/selection across related plots when it materially improves investigation.
- Keep legends close to data and unambiguous.
- Avoid smoothing raw/source data by default.
- If smoothing or interpolation is shown, label it as derived/transformed.
- Keep warning/blocking quality issues visible during analysis.

## Missing and invalid data

Never fabricate continuity.

Prefer explicit states such as:

- channel unavailable;
- mapping unavailable;
- validation blocking comparison;
- partial overlap;
- source metadata missing;
- insufficient evidence.

## High-density engineering UI

Dense is acceptable when structured.

Prefer:

- persistent context header;
- compact aligned controls;
- collapsible detail/provenance panels;
- synchronized plots;
- clear inspection cursor;
- stable spatial placement during investigation.

Avoid decorative dashboard card grids that break the engineering workflow into unrelated tiles.
