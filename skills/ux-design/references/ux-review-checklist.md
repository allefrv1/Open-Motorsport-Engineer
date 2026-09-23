# UX Review Checklist

Use this checklist when reviewing an existing or newly implemented interface.

## Task and flow
- Is the user's primary task obvious?
- Is the primary action easy to find?
- Does each screen have a clear purpose?
- Can the user recover from a wrong turn without losing work/context?
- Are destructive actions differentiated and confirmed appropriately?

## Information architecture
- Are related items grouped together?
- Is navigation predictable and consistent?
- Are labels written in the user's/domain language rather than implementation language?
- Is the current location/context visible?

## Data trust
- Are units visible?
- Are reference/baseline cases explicit?
- Are missing, invalid, partial, estimated, measured, and derived values distinguishable?
- Is provenance/method accessible when it affects interpretation?
- Are timestamps/timezones/reference frames explicit where needed?

## States
- Loading state defined?
- Empty state actionable?
- Partial-data state truthful?
- Validation warning distinguishable from blocking error?
- Error message explains what happened and what the user can do?
- Disabled controls explain why when ambiguity is likely?

## Accessibility
- Full keyboard path works?
- Focus indicator visible?
- Logical focus order?
- Accessible names on icon controls?
- Semantic headings/landmarks?
- Form labels programmatically associated?
- Errors programmatically connected to fields?
- Critical information conveyed without color alone?
- Contrast suitable for WCAG 2.2 AA?
- Content usable at zoom/reflow?
- Motion non-essential and reducible?

## Visual hierarchy
- First glance communicates what matters most?
- Typography hierarchy consistent?
- Spacing expresses grouping?
- Alignment consistent?
- Color has semantic purpose rather than decoration only?
- High-density data remains scannable?

## Responsive behavior
- Important actions/data remain available on narrow screens?
- Tables/charts have an intentional small-screen strategy?
- Touch targets remain practical?
- Comparison workflows preserve context?

## Interaction quality
- Feedback is immediate after user actions?
- Long operations expose progress/status?
- Selection/active states remain obvious?
- Filters show current state and can be reset?
- Keyboard/mouse/touch behavior stays consistent?

## Finish
Classify findings as Must Fix, Should Improve, or Polish.
