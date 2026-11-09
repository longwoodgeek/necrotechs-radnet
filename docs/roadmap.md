# RadNet roadmap

These represent experiments and design proposals, **not operational promises**.

| Workstream | Current state | Next evidence required |
|---|---|---|
| 915 MHz RNode/LoRa prototype | Successful exploratory connectivity | Controlled packet-delivery and link-budget tests |
| NomadNet Pocket BBS | Page browsing observed through obstacles | Post-recovery stability and repeated uncached page fetches |
| LinkProbe v0.1 | Code drafted on private dev branch; not live-radio-tested | Runtime audit and hardware validation before public release |
| Reticulum `rncp` file copy | Feature identified | Authenticated transfer + SHA256 comparison |
| GPS / offline UTC | Existing GPS module identified provisionally | Physical pin verification, valid GNSS fix, chrony tracking |
| Permanent Proxmox transport | Planned | VM USB pass-through, station power/UPS, backups and compliance |
| **Wi-Fi HaLow IP backhaul** | **Concept only; no equipment deployed** | Device/AP interoperability, RF coexistence and throughput/range field tests |
| SAR-oriented HaLow + LoRa node | **Research concept, not a certified SAR system** | Stakeholder requirements, redundancy, privacy, accessibility and safety testing |
| FECC/SentinelLink coordination | Architecture proposal | Human approval rules, auditing, fail-safe design |

The priority remains preserving the working BBS/RNode identities and fixing the SharkDeck filesystem before additional live testing.
