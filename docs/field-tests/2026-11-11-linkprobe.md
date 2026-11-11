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

## Original LP-007 pre-flight — before the outdoor run

**Status update:** LP-007 has now been measured; see the appended outdoor result below. This section preserves the original plan.

The original plan called for an outdoor test at approximately 200 ft (~61 m), with building and HVAC obstructions. Keep stationary peer, power, modulation and antenna conditions unchanged. Start with five 64-byte probes, 3-second minimum spacing and 15-second timeout; do a separate ten-probe repeat only if safe and connectivity holds.

Before transmitting: independently verify lawful operation for actual equipment, mode and antenna; 915 MHz and low power do not automatically establish Part 15 compliance. Check site access, weather, footing, traffic and HVAC clearance. Record hardware/software versions and deployed script hashes, antenna orientation/height, estimated distance method, obstacles and clock uncertainty. Verify the actual route uses intended LoRa interfaces and excludes IP alternatives; interface Up alone is insufficient. Preserve the managed responder and private identities.

Archive timestamped CSVs and terminal summaries with hashes, including failures, incomplete runs and route evidence. Record intended versus attempted counts, missing metrics, conditions and deviations. Publish sanitized results only after evidence exists. **This documentation work performed no radio transmissions and did not measure LP-007.**


---

# LP-007 outdoor obstructed field result — 2026-11-11

**Measured application run; operator-reported location:** approximately 200 ft (~61 m), whole apartment building and HVAC obstructed. This is an estimate, not a surveyed distance. The operator supplied the CSV and terminal screenshot after the test; this documentation session performed no transmissions.

| Metric | Result |
|---|---|
| Acknowledged probes | 10/10 |
| Payload | 64 bytes each; 640 acknowledged bytes |
| Median / maximum RTT | 426.8 / 587.3 ms |
| MacBook RX median RSSI / SNR | −92.5 dBm / +6.625 dB (displayed +6.62) |
| SharkDeck RX median RSSI / SNR | −113.0 dBm / +2.875 dB (displayed +2.88) |
| Paced application goodput | 186.56 bps |
| Elapsed duration | 27.44 seconds, screenshot-rounded |
| Pacing / timeout | 3-second minimum start interval / 15 seconds |

Counts and medians recomputed from CSV. Goodput and elapsed duration are transcribed from the matching terminal screenshot; exact monotonic elapsed duration is absent from CSV. RTT is acknowledged round-trip application latency, not one-way latency; paced goodput is not maximum on-air speed.

## Metadata correction and evidence

The new run reused the prior command: raw notes still say `LP-006 Robs room repeat; 10 probes; Mac 5mW Deck 20mW reported`, obstacles still say `furthest indoor room; interior walls`, and raw distance is blank. The operator's accompanying report corrects this run to **LP-007, approximately 200 ft outdoor/perimeter position, whole apartment building plus HVAC obstructed**. Preserve every raw cell unchanged; apply this correction only as an annotation.

The cumulative export contains the previous 20 records unchanged plus 10 new records. Total available unique evidence is now **30/30 ACK**, not 35/35. A separate five-probe outdoor starter series is not present; the documented outdoor run contains ten probes. Do not infer that all pre-flight checklist items were completed from successful ACKs.

## Screenshot reading discrepancy and interpretation

The screenshot's probe 8 Mac RSSI was initially read as −44 dBm during transcription, but the actual CSV records **−94 dBm**. Use the preserved CSV for per-probe analysis: all ten Mac readings span **−94 to −89 dBm**, with median −92.5 dBm. No CSV outlier is established. Preserve both source artifacts; do not alter the CSV to match a screenshot reading. SharkDeck readings span −115 to −110 dBm. The directional median difference is 20.5 dB; power, antennas, propagation, route or metadata behavior may contribute, without a diagnosis.

Relative to LP-006 indoors, median Mac/Deck RSSI is 17.5/15 dB weaker and median SNR is lower. All ten application probes still received matching ACKs in this particular run. This does not establish RF sensitivity margin, a range limit, zero true loss or emergency-service reliability. The small median RTT difference is not an established performance improvement.

Reported TX metadata remains +7 dBm (~5 mW) Mac and +13 dBm (~20 mW) SharkDeck, at reported 915 MHz. Actual power, antenna conditions, hardware inventory, deployed script hashes, route isolation and legal operating basis were not independently verified. No automatic Part 15 compliance claim. Retain the prior methods and limitations; successful ACKs alone do not prove a LoRa-only route.

## Follow-up

Before interpreting this as a repeatable range benchmark, record antenna orientations/heights, stationary peer position, HVAC state where safely observable, weather, distance-estimation method, radio/firmware/settings, deployed script hashes and actual route evidence excluding IP alternatives. Resolve any remaining screenshot legibility question against the original capture and CSV. Keep the existing radio settings unchanged and preserve the managed responder and private identity. Any further test remains operator-controlled and subject to site safety and independently verified lawful operation.
