# RadNet roadmap

These represent experiments and design proposals, **not operational promises**.

| Workstream | Current state | Next evidence required |
|---|---|---|
| RadNet local core v0.1 | [MacBook validation](validation/2026-11-13-macbook-pro.md): 12/12 tests; local journal verified | Repeat on other environments; no federation or authenticated identity yet |
| Terminal Interface v0.2 | [Preparation only](terminal-interface-v0.2-preparation.md); not implemented | Agree local interaction, accessibility, data boundaries and acceptance criteria before implementation |
| 915 MHz RNode/LoRa prototype | Successful exploratory connectivity | Controlled packet-delivery and link-budget tests |
| NomadNet Pocket BBS | Page browsing observed through obstacles | Post-recovery stability and repeated uncached page fetches |
| LinkProbe experimental v0.1.1-dev (operator-reported) | LP-004–LP-007: 30/30 unique application probes acknowledged across indoor and obstructed outdoor runs; see [November 11 field report](field-tests/2026-11-11-linkprobe.md). Not release-qualified. | Verify deployed source hashes, LoRa-only routing, exact spreading factor/bandwidth, firmware and hardware settings; repeat independently before a public release |
| Reticulum `rncp` file copy | Feature identified | Authenticated transfer + SHA256 comparison |
| GPS / offline UTC | Existing GPS module identified provisionally | Physical pin verification, valid GNSS fix, chrony tracking |
| Permanent Proxmox transport | Planned | VM USB pass-through, station power/UPS, backups and compliance |
| **Wi-Fi HaLow IP backhaul** | **Concept only; no equipment deployed** | Device/AP interoperability, RF coexistence and throughput/range field tests |
| SAR-oriented HaLow + LoRa node | **Research concept, not a certified SAR system** | Stakeholder requirements, redundancy, privacy, accessibility and safety testing |
| FECC/SentinelLink coordination | Architecture proposal | Human approval rules, auditing, fail-safe design |

The priority remains preserving the working BBS/RNode identities and fixing the SharkDeck filesystem before additional live testing.
