# Exploratory radio field tests — November 8, 2026

**Evidence:** Operator reports and photographs of RNode status, LXMF, and NomadNet. The original images/logs remain private. These tests were exploratory, not controlled RF certification or an operational emergency-service validation.

| Endpoint | Hardware | Operator-reported TX power |
|---|---|---|
| Portable | MacBook Pro + Heltec WiFi LoRa 32 V3 RNode | **7 dBm (~5 mW)** |
| Stationary | SharkDeck/WalnutPi + LilyGo LoRa32 RNode | **13 dBm (~20 mW)** |

Radio profile approximately 915 MHz, SF7, nominal 500 kHz bandwidth, CR 4/5. Both endpoints showed **21.88 kbps** as the radio's reported/configured rate. **That was not a measured application payload throughput.** The stationary SharkDeck Wi-Fi was deliberately turned off, but its wall clock was not synchronized.

## Observations

- **One wall, ≥20 ft:** Operator reported successful communication and NomadNet BBS browsing.
- **Two walls, ~40–45 ft estimated:** NomadNet station-information page shown as loaded. No rigorous fresh-token cache-exclusion test.
- **Outside, estimated ~200 ft, entire apartment building and HVAC in path:** Operator reported LXMF messaging worked. Screen captures supported LoRa interfaces Up, cumulative traffic growth, and a displayed one-hop link. No controlled repeated-delivery series or independent receipt log was collected.

One message had pretyped text reporting 150 feet. The operator corrected this: **that message was sent at approximately 200 feet**; the written 150-ft label was not updated before sending. It does not establish a separate 150-ft field test.

The Mac Heltec retained its small stock antenna. Antenna orientation, link budget, actual peer RSSI/SNR, EIRP, and regulatory authorization were not characterized.

## Limits and next measurements

- Cumulative traffic counters are not per-message transfer amounts or delivery percentages.
- The displayed noise floor and last interference values are **not peer RSSI**.
- No measured application goodput, RTT distribution, or packet-loss ratio is available yet.
- LinkProbe v0.1 is an experimental draft for controlled acknowledgments, RTT and goodput. It has **not been field-validated**.
- No claim of reliable rescue communication, guaranteed coverage, or certified Part 15 compliance is made.

## Replication checklist

1. Record both RF configs and antenna conditions; keep the radio path isolated.
2. Repeat uniquely labeled transmissions at fixed distances, obstacles, and powers.
3. Capture actual end-to-end acknowledgments and failures.
4. Collect packet RSSI/SNR only where software exposes true reception metadata.
5. Publish the raw data with personal locations, identifying station details, and private keys removed.

**Engineering rule:** Trust the mathematics. Verify the reality.
