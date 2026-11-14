# RadNet v0.6 — Capability Evidence & Terminal Severity

Status: design draft. No runtime capability claims or hardware probing implemented by this document.

## Principles
- A configured device is not necessarily available; a previously successful test is not proof of current availability.
- Preserve evidence as append-only events with stable IDs and local receipt timestamps. Never silently replace failed or contradictory observations.
- Distinguish capability definition, configured state, observed test result, and time-bounded operational assertion.
- Record source, method, timestamp source and uncertainty, test target, result, and any expiry/staleness policy.
- Unknown, unavailable, not configured, stale, failed, and verified are distinct states.
- Do not interpret simulation RTT as real RF measurements; do not imply emergency dispatch.
- Keep v0.5 station UUID unchanged; do not write new station identity during observation.

## Proposed capability record
- capability_id: stable machine-readable identifier (e.g. `reticulum.local`)
- label: human-readable name
- category: hardware, software, transport, or service
- configured: true/false/unknown, with evidence
- observations: append-only events with event_id, result, method, source, receipt_time, claimed_time, uncertainty, and optional expiry
- derived_state: computed view, never a mutable replacement for the underlying events

## Terminal severity palette
- GREEN: normal status, menus, successful checks.
- WHITE: information and neutral prompts.
- AMBER: warning, degraded, stale, attention needed.
- RED: actual errors, critical alerts, failed integrity verification.
- Every colored message must also have an explicit textual severity label; plain/no-color mode must retain meaning.
- Do not show red for merely unconfigured optional hardware. Red should be actionable.
- ANSI color output only on enabled color terminals; plain output has no escape codes.
- Never colorize user-supplied text as trusted terminal control sequences; sanitize or escape input.

## Acceptance tests to add
1. Append-only evidence with deterministic retrieval; no loss of prior observations.
2. Configured but untested != operational.
3. Stale evidence cannot be presented as live.
4. Simulated LinkProbe observations explicitly tagged simulation.
5. Invalid/missing capability evidence does not create or modify station identity.
6. Severity labels survive plain mode and colored mode emits appropriate ANSI SGR codes.
7. Noncritical missing optional transport is informational, not red.
8. Existing v0.5 regression suite continues to pass on Pi 5.

## Initial scope
Start with a small schema, isolated tests, and color presentation helpers. Avoid claiming live hardware state until an actual probe and freshness policy are implemented.
