# Initial Telemetry Source Feasibility

Status: **Reviewed research**

## Decision context

OME's initial source families are:

- OME CSV Exchange Profile;
- iRacing `.ibt`;
- MoTeC workflows.

This document records feasibility observations used to scope the first implementation sequence.

## OME CSV Exchange Profile

### Role

Controlled first implementation target.

### Why

- project-owned contract;
- deterministic fixtures;
- easy inspection;
- no vendor dependency;
- useful for validating ingestion/provenance boundaries.

### Limitation

It is intentionally not the canonical internal model and does not attempt to represent arbitrary multi-rate acquisition losslessly.

## iRacing .ibt

### Evidence

iRacing documentation describes telemetry being saved to disk and identifies `.ibt` as the iRacing binary telemetry file format.

iRacing has also published SDK support for reading telemetry files.

References:

- iRacing telemetry quickstart: https://ir-core-sites.iracing.com/dev/atlas/atlas_quickstart.pdf
- iRacing release notes describing disk-client support: https://www.iracing.com/2016-season-3-release-notes/

### Architectural conclusion

`.ibt` is suitable as the first external binary adapter target.

It provides a useful development source with richer metadata than a controlled CSV fixture.

It must not define OME's canonical channel model.

## MoTeC

### Evidence

MoTeC i2 supports exporting channel data for an outing, lap or selected area to CSV.

MoTeC's i2 API can load `.ld` files and read channels, laps, beacons and details.

The i2 API is a licensed feature and uses COM-compatible access, creating platform/licensing constraints for an open-source cross-platform core.

References:

- MoTeC i2 product page: https://www.motec.com.au/products/I2
- MoTeC i2 API User Guide: https://website.motec.com.au/hessian/uploads/i2_API_User_Guide_330ed28c83.pdf

### Architectural conclusion

For the first OME vertical slice:

**MoTeC CSV export is the supported professional real-motorsport path.**

Native `.ld` ingestion is deferred to an optional adapter/integration decision.

OME's portable core must not depend on the licensed i2 COM API.

## ASAM MDF reference

ASAM MDF demonstrates important measurement-data capabilities:

- metadata stored with measurements;
- multiple/non-periodic sampling rates;
- source/acquisition identity;
- conversion information;
- events and attachments;
- synchronization domains.

Reference:

- https://www.asam.net/standards/detail/mdf/

OME does not need to adopt MDF for the first vertical slice.

MDF is an architectural reference showing why a flat CSV should not become OME's canonical internal telemetry model.

## Initial support order

1. OME CSV Profile
2. iRacing `.ibt`
3. MoTeC CSV export
4. evaluate native MoTeC `.ld`
5. consider MDF/MF4 and other professional adapters later

## Conclusion

This sequence gives OME:

- a controlled test source;
- a rich external development source;
- a real-motorsport professional workflow source;

without locking the project to a proprietary API or one vendor's data model.
