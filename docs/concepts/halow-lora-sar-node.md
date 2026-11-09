# Concept: Wi-Fi HaLow backhaul with independent LoRa heartbeat

**Status: EARLY CONCEPT, NOT DEPLOYED OR FIELD VALIDATED.** This is a volunteer maker exploration, not a public-safety-grade system.

## Purpose

Provide useful **local Wi-Fi connectivity** and a **longer-range wireless IP backhaul** to remote teams when commercial infrastructure is unavailable, while preserving a distinct **low-data-rate status and messaging path** when that backhaul fails.

~~~text
[Team phones / tablets]
           |
    Standard 2.4/5 GHz Wi-Fi
           |
[Portable router/AP + local services]
           |
        Ethernet
           |
 [Wi-Fi HaLow bridge]  === 802.11ah IP backhaul ===  [HaLow base bridge]
           |                                            |
           +-- [Host: heartbeat agent]                 [Command/base LAN]
                  |
           [Independent 915 MHz RNode] ~~~ LoRa ~~~ [Base RNode]
                  |
           [Optional GNSS, battery/UPS]
~~~

Ordinary phones and laptops do **not** normally contain HaLow radios. The team's conventional Wi-Fi access point bridges to purpose-built HaLow equipment. An additional HaLow relay or mesh topology is not automatic; it needs specifically supported equipment and configuration.

## Planes

- **Data plane (HaLow/IP):** web-based maps and forms, local documents, low-bandwidth situational updates, larger configuration transfers, ordinary network applications, and Reticulum over a configured IP interface.
- **Status plane (LoRa):** compact, authenticated heartbeat with node ID pseudonym, sequence number, observed time and time confidence, radio/battery health, HaLow backhaul state, availability of local services, and optional GNSS fix quality. Send only minimum necessary telemetry.
- **Degraded mode:** If HaLow fails, do **not** magically promise IP service over LoRa. Keep critical text/status packets small. Explicitly tell clients the data plane is unavailable; allow a separate approved LXMF / Reticulum text workflow.

## Heartbeat design (research draft)

Example *logical fields*, not a fixed packet encoding:

~~~text
version | node_alias | boot_id | sequence | time_quality
power_pct | halow_link_state | wifi_ap_state | rnode_state
gps_fix_state | role_flags | authenticated_integrity_tag
~~~

A starting design might send a sparse heartbeat every **5 minutes**, later adapted based on duty-cycle, node count and mission needs. Do not broadcast frequent Reticulum announces as a substitute for dedicated heartbeat messages; Reticulum's documentation generally advises much lower announce frequency. At the receiver, stale or missing heartbeats become **'unknown / last heard'**, not automatic evidence that people are in distress. Detect a genuine backhaul failure with link-level health checks, not a single failed ping.

## Practical constraints and safeguards

- **Spectrum overlap:** U.S. HaLow and many LoRa devices can both use 902–928 MHz. They do not demodulate each other. RF desensitization/interference is possible; test antenna separation, channels, traffic load, receiver blocking, and actual authorized configurations. A LoRa control plane sharing the same band is **logically independent** but **not fully RF-independent**.
- **Failover:** Wi-Fi HaLow is an IP backhaul. LoRa should be a separately configured, constrained messaging/status route, **not** a transparent replacement for high-bandwidth Wi-Fi.
- **Power:** independent battery-backed operation and brownout recovery are important, particularly after the SharkDeck's unrelated storage event.
- **Privacy and authentication:** rotate/pseudonymize field aliases, authenticate peers, protect personal location data, and avoid recording responder locations unnecessarily.
- **Safety:** no automated dispatch, geolocation certainty, rescue assurances or human-status inference from missing heartbeats. Train with SAR partners and test against their actual procedures before any field reliance.
- **Regulation:** Part 15 requirements depend on actual hardware grants, RF configuration, antennas and operating mode. No compliance claim has been made.

## Proof-of-concept ladder

1. **Bench:** Two HaLow bridges with local ordinary Wi-Fi AP, offline-only IP, and local web service. Verify exact network path and usable throughput.
2. **Resilience:** Add two LoRa RNodes and a dedicated heartbeat application. Test out-of-band status with HaLow intentionally unplugged or switched off.
3. **Coexistence:** Test HaLow under load and measure LoRa message success. Avoid assuming two 900 MHz radios never interfere.
4. **Field:** Short controlled distances first, then trees, hills, and foliage; record both technology links and antenna positions, with permission and land-access compliance.
5. **Human factors:** SAR volunteer review, accessibility checks, permissions, power/thermal tests, data retention, explicit failure indicators, and operator training.

## References

- [IEEE 802.11ah / Wi-Fi HaLow summary and PHY data rates (IEEE PDF)](https://engagestandards.ieee.org/rs/211-FYL-955/images/02_IEEE%20Next%20Gen%20Connectivity%20Workshop%20802-11%20standards02072023.pdf)
- [Wireless Broadband Alliance — HaLow field trials](https://wballiance.com/wi-fi-halow-for-iot-field-trials-report/)
- [Reticulum physical interface documentation](https://reticulum.network/manual/interfaces)
- [Inter-protocol coexistence study (Sensors, 2025)](https://www.mdpi.com/1424-8220/25/22/6924)
