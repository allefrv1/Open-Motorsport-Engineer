# Session, Run and Lap Context

Status: **Accepted initial domain model**

## Purpose

Telemetry gains meaning from operational context.

OME must not treat a Lap as an isolated array of samples.

## Event

An Event groups related motorsport activity at a venue/circuit.

## Session

A Session is a bounded period of track activity with a coherent operational purpose, such as practice, qualifying, race or test session.

A source file may contain all or part of one Session. OME must not assume a one-file-to-one-session relationship universally.

## Run / Outing

For the initial OME model, **Run** is the preferred project term for a continuous operational outing of a vehicle within a Session, typically bounded by leaving and returning to the pit/working context.

"Outing" may be retained as source terminology or an alias when required by a source ecosystem.

## Stint

Stint is not treated as a strict synonym for Run.

It is reserved for category/workflow-specific continuous operating periods whose boundaries may differ from pit-out/pit-in semantics.

The exact Stint model is deferred until strategy/endurance requirements need it.

## Lap

A Lap belongs to a Session and normally to a Run.

A Lap should be capable of carrying:

- source lap identifier when supplied;
- lap number within context;
- start/end reference;
- timing information;
- validity/quality information;
- provenance.

## Import boundary

Importers may preserve source-provided session/run/lap markers and events.

Importers must not invent generic lap segmentation when the source does not provide sufficient evidence.

## Organization responsibility

Canonical Session / Run / Lap organization is a separate responsibility from raw source parsing.

For the first vertical slice:

- source-provided lap markers may be used when trustworthy;
- OME CSV fixtures may explicitly define lap context;
- generic automatic lap detection is deferred.

## Context association

A Run may be associated with:

- driver;
- vehicle;
- setup version;
- tyre set;
- fuel/energy state;
- run plan;
- driver feedback;
- conditions.

These associations should not be forced into raw telemetry channels.

They are operational context.
