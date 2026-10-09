# UX / Accessibility Review — Plan 032 Interactive Engineering Telemetry Workspace

Date: 2026-10-09

Related PR: #81

Decision: **READY — source and CI acceptance complete**

## Task and information architecture

- Compact persistent source setup with explicit Controlled OME CSV / Traqmate selection.
- Lap A remains reference; Lap B remains candidate; B-A sign and distance unit remain explicit.
- Analysis summary precedes chart inspection, observation preview, evidence inventory and provenance.
- No simulated chart data or fictitious source states are shown before successful analysis.
- Full chronological observation list remains available through an explicit show-all action.

## Plot interaction

- Plotly retains one distance axis across all displayed channels.
- Delta is not toggleable and retains the backend-returned series and seconds unit.
- Each available source overlay can be hidden/restored; unavailable channels cannot be selected.
- Lap A is solid, Lap B dashed, and discrete gear continues using stepped lines.
- Keyboard slider selects exact distance-grid points. Plot click selects a returned point only,
  never an interpolated point between samples.
- View controls change only the viewport; they do not change the report or re-run engineering.
- Export through Plotly's native image toolbar is a presentation action, not a new data product.

## Accessible and honest states

- Form fields, group labels, submit button, zoom buttons and channel checkboxes remain semantic.
- Active selection and focus-visible outlines are present.
- Screen reader labels identify the inspection region and slider.
- Missing Evidence remains in Supporting evidence and cannot be mistaken for zero.
- A channel's measured/derived scientific status is *not* inferred from a transport overlay kind:
  the UI calls these channels source overlays and labels only the backend-computed delta as derived.
- Loading, network errors and not-ready stages keep text and recovery paths.
- Responsive layout stacks inputs and scrolls charts horizontally rather than compressing axes.
- Unnecessary motion is reduced under `prefers-reduced-motion`.

## Test evidence

- TDD RED: PR CI run for commit `bb234d9` failed specifically for missing channel
  checkboxes, exact-value slider, zoom controls and derived-delta identity.
- Existing frontend regression tests cover OME CSV and physical Traqmate requests,
  Missing Evidence, delta B-A, provenance and not-ready states.
- CI GREEN: OME CI run `37892682883` on final PR #81 head. Canonical harness and container verification both passed.

## Limitations and risks

- No local browser screenshot/rendering was possible because repository clone could not resolve
  GitHub from the execution container. This review covers source/test contracts, not
  visual pixel inspection in a real browser.
- Manual desktop/mobile visual inspection is recommended after merge, especially plot toolbar
  wrapping, 200% zoom, and hover contrast.
- No new tyre/physics/vehicle engineering decisions are made; multidisciplinary domain review
  is not required for presentation-only work.

## Exit gate

PR #81 merged to `main` as `087163e400fae8570ee79ab0692ccf6a0700203a` after full CI GREEN.
The remaining manual browser visual QA is explicitly noted as a follow-up, not hidden as completed evidence.
