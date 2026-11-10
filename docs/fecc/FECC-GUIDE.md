# FECC Unified Field Guide — v0.1 (architecture baseline)

**Project:** FECC / SentinelLink / Links / RadNet / optional ROSETTA integration  
**Established:** 2026-11-10  
**Status:** DESIGN BASELINE + EXPERIMENTAL COMPONENTS. **NOT** an operational emergency service, certified rescue system, guaranteed distress route, or approved source of medical instructions.  
**Public home:** [NecroTechs RadNet](https://github.com/longwoodgeek/necrotechs-radnet)  
**Private engineering home:** SentinelLink repository (details and evidence restricted to authorized collaborators)  
**Maintainers:** NecroTechs project operators, with AI-assisted drafting acknowledged and human review required.  
**Guide version:** 0.1.0

> **Purpose:** A unified vocabulary, architecture, evidence standard and development framework for independent FECC Cores, portable CyberDeck consoles and specialized SentinelLink **Links**. This guide is mirrored into the related repositories; changes should update both mirrors in the same review cycle. Repository-specific details belong in separate addenda, not conflicting versions of this baseline.

## 1. Mission and safety charter

Investigate repairable, affordable, offline-first infrastructure that can exchange information and facilitate human coordination when ordinary networks are absent or degraded.

**Maximum curiosity. Measured power.** If lives are on the line, maximum effort remains bounded by safe, accountable operation.

Foundational rules:

- **Help first, information second:** Do not impose registration to preserve an initial request for assistance.
- **Never fabricate success:** “Saved locally,” “queued,” “relay received,” “human acknowledged,” “assigned,” “dispatched,” and “resolved” are different, auditable claims.
- **No Dahak deadlock:** Absence of an IC or central authority cannot block local recording and permitted emergency relay. Narrow emergency delegation may be possible, but never grants permanent unlimited power.
- **Evidence before certainty:** Preserve unverified reports and contradictions, label them, and verify active safety decisions promptly.
- **Safety of people over equipment:** Do not send civilians or volunteers into unverified flood, electrical or structural hazards to reach a device.
- **Local-first and accessible:** A unit remains useful when disconnected and must expose honest limitations when offline.
- **Safety-critical behavior must not require an LLM:** Assistance dialogue can eventually use bounded, reviewed content; command decisions and dispatch claims remain verifiable and human-accountable.

## 2. Unified nomenclature

| Term | Definition | Independence / authority |
|---|---|---|
| **FECC** | Field Emergency Communications Computer: the overall modular field communications/incident-support architecture | An ecosystem, **not** a single laptop |
| **FECC Core** | Always-on or unattended-capable local server (e.g. mini-PC, SBC, or VM) hosting durable records, policy, scheduler, gateway and portal services | Operates with no CyberDeck docked; no Internet required for local functions |
| **FECC Console / CyberDeck** | Portable operator console with displays, controls, diagnostics, local cache and radio options | Extends a Core when connected; can enter limited standalone/emergency-Core mode when disconnected |
| **Link** | A field endpoint carrying a subset of sensing, communication, public assistance, cached data or relay capabilities | Operates to its own advertised capabilities; may be headless |
| **SentinelLink** | Software/application/protocol family for incident records, roles, messaging, resource discovery, authorization, federation and Links | Services can run on Core or bounded Edge |
| **RadNet / NomadNet** | Complementary low-bandwidth BBS/knowledge-sharing environment | Not synonymous with emergency dispatch |
| **ROSETTA** | Optional preservation-first language/translation and interpretation service | Failure must not block original-language information or help requests |
| **CIDERTEA / SDRTE** | Scenario → Decision → Requirement → Test → Evidence | Research and validation workflow |

### Link capability subtypes (combinable, not mutually exclusive)

- **Fixed Link:** unattended relay, heartbeat, resource cache or sensor node.
- **Camp / Public Assistance Link:** accessible emergency button, public information and messaging interface, speaker/microphone/display where provisioned.
- **Mobile Link:** vehicle, carried or temporary-deployment node.
- **Floating / Buoyant Link:** proposed water-tolerant node for *controlled* deployments; not a license for hazardous swift-water improvisation.
- **Aerial Link / ALINK:** proposed airborne relay/observation equipment (drone payload, tethered aerostat, or suitable VTOL station-keeping). Flight safety, airspace, RF legality, failover and actual endurance must be measured.
- **Drop Link:** proposed protected deployable pod, distinct from an airborne relay; no untested aerial release.
- **Locker Link:** proposed secure outdoor cache of an accessible CYD/terminal with monitored charge and **independent emergency access**.
- **Utility Link / Liaison Terminal:** authorized exchange of hazard reports with a utility or infrastructure partner; **never** autonomous control of utility switchgear.

A Link announces only its actually enabled capabilities, transport, resource constraints and time-limited status. Names describe roles, **not** proof of tested features.

## 3. Components and responsibilities

```text
        [Trusted / optional federated FECC Core peers]
                           ^  |
                  scoped, audited exchange
                           |  v
  [OpenWrt/LAN/HaLow gateways] <----> [FECC CORE mini-PC]
                                        |  durable records
  [Browser/PWA/APK clients] <---------->|  identity + policy
  [CYD role-based terminals] <--------->|  scheduling + escalation
  [CyberDeck / FECC Console] <--------->|  incident + resource portal
          |                             |  Reticulum/transport gateways
   standalone local cache              |
          |                      [Transport adapters]
          +-----------------------+----+----+
                                  |         |
                            LoRa/RNode   IP/Wi-Fi/HaLow
                                  |         |
                             [LINK FLEET]---+
```

Core services: SQLite or another durable local storage layer; append-only event/outbox history; unique event/incident/request IDs; identity & authorization; incident resource registry; message queues; scheduler; federation/transport adapters; human audit log; optional web portal.

**No CyberDeck dependency:** Removing a CyberDeck must not interrupt Core's intake, local resource service, scheduled node checks, offline queues, or authorized responder notifications. A CyberDeck that loses Core contact may preserve observations and continue bounded local services but does not acquire extra operator authority.

**No single-Core dependency:** If a Core fails, individual capable Links still log requests and attempt delivery to other trusted peers via available paths. Degraded modes must be explicit.

## 4. Network and service capability ladder

| Link available | Appropriate service level | Caution |
|---|---|---|
| Local Ethernet / standard Wi-Fi | Full web portal, operator UI, richer maps, files, incident views, attachments if supported | LAN access is not operator authorization |
| Wi-Fi HaLow backhaul through compatible gateway | IP service subset chosen by measured capacity/power | Ordinary ESP32/CYD Wi-Fi cannot directly attach to HaLow |
| LoRa via RNode / Reticulum | Compact distress, ack, heartbeat, text-oriented BBS and summaries | Low-rate, airtime budget, regional radio rules; not full-web transport |
| No connectivity | Locally cached resources, event capture, truthful queued status, later sync | Never say “delivered” when only saved |

Collect sensor state and publish/synchronize it on different schedules. Separate machine heartbeat, human welfare check-in and task/assignment progress. Use jitter, congestion control, prioritization and power budgets. Treat a device “online” as different from a person “safe.”

## 5. Operator authority and federation

- People have scoped, authenticated permissions; terminals alone never grant IC status.
- Incident-specific delegations follow the org chart; ad hoc incidents route approvals to IC until explicit supervisory structure exists.
- Provisional emergency coordination cannot become permanent leadership through accidental privilege escalation.
- Responder capability claims are **Self-Declared**, **Locally Attested**, or **Externally Validated**, **per qualification**. Selected organizations must actually verify and sign attestations before representing them as verified.
- Federation peer *discovery* is distinct from federation *trust* and *data sharing*. Explicit, logged allow/deny policies determine what each partner may see; protect personal and infrastructure-sensitive data.
- Escalation widens notification without erasing the original recipient; late responses need conflict-safe resolution.
- Command, responder assignments, and welfare transfers require accountable human decisions appropriate to the emergency.

## 6. Emergency intake and state semantics

Sequence: minimal anonymous HELP -> durable local receipt -> route/delivery attempts -> human acknowledgment -> assignment/dispatch if actually authorized -> field outcome -> human-verified closure.

Track requester communication status and incident severity **separately** from per-message communications priority.

Suggested request state vocabulary (to be refined and tested):
`RECEIVED_LOCAL`, `QUEUED`, `RELAY_RECEIVED`, `DELIVERED_TO_STATION`, `ACKNOWLEDGED_BY_HUMAN`, `ASSIGNED`, `RESPONSE_CONFIRMED`, `CLOSED`.
These are distinct *events*, not an assumption that every request passes through one linear state. Captured evidence must show who confirmed each state. Provisional incidents and urgent **unverified** alerts are supported.

If civilian devices or Link battery degrade, show last update and remaining capability honestly; don't silently display stale status as current.

## 7. Translation and international profiles (ROSETTA optional)

The base protocol and event schema should be locale-neutral (stable IDs, timestamps with UTC and clock-confidence metadata, language tags, original-source preservation, local coordinate reference system, time zone and units). Region profiles supply:

- Legal radio frequency/power/airtime settings; regulatory approval evaluated independently for each deployment region.
- Local emergency numbers, authority model, safe-use instructions, privacy and credential policies.
- Language packs, fonts, offline maps/resources and reviewed emergency terminology.
- International and local organizations for requested signed attestations.
- Map labels and photographed sign interpretation, with original text, source image and translation confidence kept together.

**ROSETTA should assist human interpretation, not become authoritative.** Keep source images/text, identify ambiguous place names, surface low confidence, and require human or pre-reviewed guidance for consequential decisions. No translation failure can block the original emergency request.

## 8. Build profiles and preliminary acceptance gates

**A. Software-only alpha** — simulated events, local API/UI, offline SQLite, incident receipt/ACK/escalation, responder registry, audit trail. No external dispatch.

**B. Bench FECC** — standalone Core (candidate dedicated mini-PC), independent CyberDeck UI, separate Link simulator; test connection loss and application restart.

**C. Controlled radio lab** — RNode/Reticulum transport, packet acknowledgment, reproducible loss/latency and power measurements, and offline resynchronization. Distinguish reported configured radio rates from real measured application throughput.

**D. Multi-site field pilot** — only with authorized participants, site consent, legal RF settings, controlled simulated incidents and safety review.

**E. Real emergency partner use** — requires independent security and safety assurance, organizational agreements, legal/regulatory review, accessibility evaluation, exercises with actual responders, operational support and clearly documented limits.

Suggested metrics: accepted request durability, end-to-end delivery latency and success rate, relay/ACK correctness, message size and airtime, transport recovery, conflict rates, battery runtime, operator task time, accessibility, and translation error severity.

## 9. CIDERTEA research protocol

For every hypothesis and design scenario:

1. **Scenario:** Objective, environment, threat/failure model, assumptions and simulation/physical boundary.
2. **Decision:** Chosen tradeoff and owner, alternatives and reasons.
3. **Requirement:** Unique ID, observable behavior, safety constraints and priority.
4. **Test:** Repeatable setup, inputs, expected results, negative cases, measurement method.
5. **Evidence:** Logs/screenshots/checksums/measurements, provenance, limitations and whether a human witnessed the behavior.

Never substitute imagined tabletop outcomes for real-world evidence. Label result maturity as `PROPOSED`, `SIMULATED`, `IMPLEMENTED_UNTESTED`, `BENCH_OBSERVED`, `MEASURED`, `INDEPENDENTLY_VALIDATED`, or `DEPLOYED_APPROVED` (the last requiring explicit outside approval).

A public research entry must be reviewed for redaction before release; private records can retain additional test context under need-to-know access, but **do not commit private keys, credentials, identifiable patient information or raw security secrets even privately**. Store sensitive evidence outside git and reference safe identifiers.

## 10. Guide governance and next work

- This **public unified guide is the canonical conceptual baseline**, with a matching private mirror for offline development. Version both together; if they diverge, reconcile before changing implementations.
- Private repository: detailed unresolved architecture, test harnesses, full CIDERTEA scenario checkpoint, code change plans and sanitized evidence pointers.
- Public repository: human-reviewed hypotheses, reproducible protocols, aggregated/anonymized measured results and clear limitations.
- Changes affecting incident intake, authorization, delivery claims, power survival or hazard handling require adversarial scenario tests and human review.
- Next engineering milestone: a **Core-without-CyberDeck** test, followed by **CyberDeck-as-bounded-standalone-Core** and a controlled ROSETTA translation experiment.
- Do not merge or conflate independently developed Reticulum, RNode, NomadNet, HaLow or external translation projects; respect their licenses and attributions.

## Related public references
- [RadNet prototype architecture](../architecture.md)
- [RadNet field-test notes](../field-tests/2026-11-08-radio-tests.md)
- [Engineering charter](../engineering-charter.md)
- [Radio/regulatory notes](../radio-and-regulatory-notes.md)
