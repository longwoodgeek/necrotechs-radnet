# LinkProbe indoor results and LP-007 pre-flight — 2026-11-11

Experimental, small-sample field observations from operator-supplied CSV exports and terminal screenshots. Raw evidence is preserved privately with SHA-256 hashes; no station identities, addresses or internal endpoints are published.

| Test | Placement | ACK | Median RTT ms | Mac RX dBm / SNR dB | SharkDeck RX dBm / SNR dB | Paced goodput bps |
|---|---|---|---|---|---|---|
| LP-004 | Bedroom to living room, one interior wall | 5/5 | 505.5 | -64 / +9.75 | -86 / +7.0 | 205.90 |
| LP-005 | Furthest indoor room, stationary living-room peer | 5/5 | 456.7 | -74 / +10.25 | -97 / +6.5 | 205.27 |
| LP-006 | Same furthest indoor room, repeat | 10/10 | 453.0 | -75 / +9.38 | -98 / +6.75 | 186.34 |

**Evidence correction:** LP-004's raw note says “same-room baseline”; the operator corrected this to bedroom/living room with one interior wall. The raw export is unchanged. The exports are cumulative (5, 10 and 20 rows); deduplicating matching run ID + sequence yields **20/20 unique acknowledged probes**, not the previously stated 25/25. No additional five-probe run is established.

All runs used 64-byte payloads, 3-second minimum start spacing and 15-second timeout. Counts and medians were recomputed from CSV; paced goodput is transcribed from matching screenshots, whose elapsed durations are 12.43, 12.47 and 27.48 seconds. The CSV lacks full-precision monotonic elapsed duration, so goodput cannot be exactly reconstructed from its rounded UTC labels.

RTT is acknowledged round-trip application latency measured on the client monotonic clock, not one-way latency. Paced goodput includes deliberate waiting and is not maximum on-air speed. No observed failed ACKs in 20 probes does not prove a zero underlying packet-loss rate, coverage guarantee or emergency-service reliability.

MacBook HelTec V3 power is operator-reported 5 mW (~+7 dBm), SharkDeck ~20 mW (~+13 dBm), at reported 915 MHz; actual physical settings are unverified and unchanged. Current operator report identifies HelTec V3 at both stations; older project material identified LilyGo at SharkDeck, an inventory discrepancy to verify. Directional RSSI medians differ 22–23 dB; power, antennas, propagation and other factors may contribute, without a diagnosis. RX metadata may describe final-hop reception; LoRa-only routing was not independently proven by these exports. Clock accuracy is unverified.

Operator reports patched v0.1.1-dev on both stations, managed responder active with stable identity, and Reticulum/NomadNet/ATLAS service operational. This is reported state, not a fresh remote service check. Repository/deployed source equivalence remains unverified; no release qualification is implied.

## LP-007 — planned, unmeasured

Later outdoor test at approximately 200 ft (~61 m), with building and HVAC obstructions. Keep stationary peer, power, modulation and antenna conditions unchanged. Start with five 64-byte probes, 3-second minimum spacing and 15-second timeout; do a separate ten-probe repeat only if safe and connectivity holds.

Before transmitting: independently verify lawful operation for actual equipment, mode and antenna; 915 MHz and low power do not automatically establish Part 15 compliance. Check site access, weather, footing, traffic and HVAC clearance. Record hardware/software versions and deployed script hashes, antenna orientation/height, estimated distance method, obstacles and clock uncertainty. Verify the actual route uses intended LoRa interfaces and excludes IP alternatives; interface Up alone is insufficient. Preserve the managed responder and private identities.

Archive timestamped CSVs and terminal summaries with hashes, including failures, incomplete runs and route evidence. Record intended versus attempted counts, missing metrics, conditions and deviations. Publish sanitized results only after evidence exists. **This documentation work performed no radio transmissions and did not measure LP-007.**
