# Public Research Log — FECC / SentinelLink / RadNet

**Scope:** Public-facing, reviewed experimental and architectural record. This log is not an emergency service and is not a source of real-time operational status.

## Start here

- [Unified FECC guide v0.1](../fecc/FECC-GUIDE.md): common vocabulary, architecture, roles, safety, evidence protocol and internationalization.
- [2026-11-10 — FECC Core/CyberDeck/Link baseline](2026-11-10-fecc-baseline.md): first research entry.
- [Experiment template](EXPERIMENT-TEMPLATE.md): standardized CIDERTEA evidence record.
- [November 2026 radio observations](../field-tests/2026-11-08-radio-tests.md): existing exploratory LoRa/Reticulum findings.
- [RadNet recovery log](../recovery/operation-phoenix-2026-11-09.md): existing recovery event.

## Publication rules

1. State **whether each entry is proposed, simulated, bench-observed, measured, independently validated, or approved for deployment**. Never report simulated scenario behavior as field-tested software.
2. Separate **hardware inventory**, **configured settings**, **operator-observed behavior**, **quantitatively measured results**, and **unresolved assumptions**.
3. Prefer repeatable tests with dated raw evidence held privately; public results link to sanitized, reviewable summaries.
4. Do not post real distress reports, live station identities, authentication tokens, addresses of vulnerable locations, private frequency/access configurations, personal medical data, or uncontrolled access information.
5. Preserve negative results, failed tests, and methodological changes; no deleting inconvenient observations.
6. Attribute operator reports and AI-assisted drafting. Human review is required before claims of safety, conformance, or use with real responders.

## Study IDs and naming

- **FEC-R-YYYY-NNN** — research experiment (e.g., FEC-R-2026-001).
- **SDRTE-NNN** — CIDERTEA tabletop scenario; simulated unless separately field-tested.
- **REQ-...** — requirement; **TEST-...** — specific reproducible acceptance test.
- Version protocol and hardware profiles independently of prose dates.

## Current validated boundary

- Public Reticulum/LoRa/NomadNet results are **exploratory operator observations**, not controlled throughput or rescue reliability measurements.
- FECC dual-screen local console has been **operator-observed**; no certified mission-critical FECC service has been demonstrated.
- Independent FECC Core, federated incident workflows, ROSETTA-assisted translation, aerial/floating Links, and partner utility federation are architectural proposals, not validated deployments.

## Immediate experiment queue

1. FECC Core runs unattended with the CyberDeck physically disconnected.
2. CyberDeck survives Core outage in bounded standalone mode, without silently granting command authority.
3. Durable anonymous HELP submission and honest status transitions during loss and return of connectivity.
4. LoRa application-level delivery, measured loss/latency/airtime and queued delivery resumption.
5. ROSETTA translation pilot: preserve originals; report uncertainty on maps/signs and compare to human-reviewed reference translations.
