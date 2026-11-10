# FEC-R-2026-001 — FECC Architectural Baseline

**Date:** 2026-11-10  
**Visibility:** PUBLIC (sanitized summary)  
**Status:** ARCHITECTURAL PROPOSAL with clearly separated operator-observed prototypes  
**Authors/attribution:** NecroTechs project direction and reported observations; AI-assisted synthesis/drafting, with human testing required.

## Scenario / research motivation

A portable command console should not be the sole infrastructure for accepting local requests or providing emergency information. Can a low-cost standalone FECC Core remain functional without a CyberDeck, while Links and a separate language service extend utility over varying networks and regions?

## Decision

Adopt the following distinction:
- **FECC Core:** durable local mini-PC/SBC/VM services, no docked CyberDeck required.
- **CyberDeck / Console:** portable interface, field diagnostics and a bounded standalone fallback.
- **Links:** modular unattended/mobile/public-aid nodes with declared capabilities and transport limits.
- **SentinelLink:** software coordination and federation functions.
- **ROSETTA:** optional original-preserving translation aid, not emergency authority.

See [Unified FECC guide](../fecc/FECC-GUIDE.md).

## Previously observed evidence (not from this proposed test)

- Operator-observed radio messaging and NomadNet page browsing through interior obstacles; an estimated ~200-foot obstructed test was reported. See the existing [radio test report](../field-tests/2026-11-08-radio-tests.md) for caveats.
- A Raspberry Pi 5 development CyberDeck displayed live system telemetry on an HDMI monitor and a separate 320x240 GPIO/SPI control display. Mouse input on the control page was observed to change the main dashboard; touchscreen calibration/fit remained in progress. This demonstrates a two-display user-interface proof of concept, **not** standalone Core, emergency dispatch or reliability.
- A failed removable-media filesystem prompted a successful operator-reported staged file evacuation to another device; backup consistency and final restoration require separate verification. See [Operation Phoenix](../recovery/operation-phoenix-2026-11-09.md).

## Hypotheses (not outcomes)

H1: A dedicated local FECC Core can maintain event storage, public help interface, message queues and schedules during complete CyberDeck disconnection.

H2: A disconnected CyberDeck can capture observations and limited local help requests without elevating its operator privileges, then synchronize safely.

H3: Local Wi-Fi, IP/HaLow gateways, low-bandwidth LoRa/Reticulum and cached resources can expose different service representations without inventing delivery confirmations.

H4: A separate translation tool can help interpret signs/maps/incident text while preserving original source and highlighting uncertainty; failures will not block core services.

## Proposed test sequence

**TEST-FEC-001 Core independence:** Run a Core with synthetic incident data, disconnect CyberDeck for a controlled interval, submit anonymous simulated help, and verify local durability/queueing. Repeat through power/restart.

**TEST-FEC-002 Standalone Console:** Disconnect Core mid-operation; verify limited offline capture, zero privilege escalation, visible staleness and conflict-safe eventual merge.

**TEST-FEC-003 Transport adaptation:** Replay identical compact request/update events through simulated IP and limited LoRa transports. Measure delivery latency, size, retries, congestion and radio duty cycle on hardware later.

**TEST-FEC-004 Translation source preservation:** Capture an authorized sample map label and public sign, translate in a controlled environment, compare with reference translation and verify original remains available during translator failure.

## Evidence to collect

Software versions and commit SHAs; approved hardware models (not station identifiers); sanitized topology; test inputs; UTC timestamp and clock sync confidence; raw logs stored privately; public aggregate delivery/recovery tables; failures; operator-observed and independently measured distinctions.

## Current result

**NOT RUN.** This entry freezes hypotheses and acceptance methodology. It does not claim that the independent Core, autonomous incident workflow, or translation functionality already exists.

## Safety and constraints

No real emergency requests, real responder records, credential material or unauthorized RF/utility control. International deployments require local radio, privacy, accessibility, mapping and public-safety approval checks.

## Next action

Implement a deterministic, local-only test harness and durable incident record on a dedicated Core candidate. Record all outcomes—successful or failed—under a new dated test entry.
