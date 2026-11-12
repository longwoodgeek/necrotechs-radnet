# LinkProbe 0.2-dev — shareable offline tooling

**Status:** experimental development tool, not a release-qualified radio benchmark.

This repository now includes a portable Python standard-library CLI at [`tools/linkprobe.py`](../../tools/linkprobe.py). It currently supports **synthetic** probe generation and summary of its own schema-v1 CSV exports. **It does not transmit radio packets, implement Reticulum/LXMF, or reproduce the operator's patched 0.1.1-dev field probe.** The deployed field scripts and hashes have not been verified. Never describe simulated samples as observed RF results.

## Quick start

Python 3.10+:

```sh
python tools/linkprobe.py simulate --count 10 --payload-bytes 64 --seed 42 --loss 0.1 --output evidence/synthetic-lp001
python tools/linkprobe.py summarize evidence/synthetic-lp001.csv
python -m unittest discover -s tests -v
```

The generator creates a unique run ID, UTC labels, synthetic ACK/RTT fields, and an evidence CSV with a companion JSON containing its SHA-256. It refuses to overwrite either output file. Fixed seeds reproduce simulated outcomes, not timestamps or run IDs. Simulation RTT is a modeled number; it is **not** measured by waiting on a network. The summary intentionally omits goodput when the source CSV lacks a verified monotonic run duration.

## Evidence contract (schema v1)

`schema_version,run_id,sequence,started_utc,elapsed_monotonic_s,payload_bytes,acknowledged,rtt_ms,error,mode`

Deduplication uses `run_id + sequence`; duplicates are rejected rather than silently dropped. UTC is a label and clock accuracy is not inferred. RTT means application-level acknowledged round trip. Paced goodput, when a reliable elapsed duration is supplied, includes intentional inter-probe waiting; it is not raw RF bitrate.

**Do not import the November 11 field CSV directly**: its schema differs and its source metadata contains documented corrections. An explicit, tested, non-destructive legacy adapter is needed first. Preserve raw evidence and hashes.

## Next work before real-radio release

1. Recover the actual deployed 0.1.1-dev client/responder sources and verify their hashes without disclosing private station identities.
2. Define a signed or integrity-checked application probe envelope with run ID, sequence, payload size and nonce; implement matching ACKs, timeout accounting, bounded retries, and interruption-safe partial exports.
3. Add an opt-in Reticulum adapter; never infer LoRa-only routing from interface-up status or ACK alone.
4. Capture verified spreading factor, bandwidth, coding rate, frequency, firmware, power, antenna, interface path, and route evidence; mark unavailable fields `unknown`.
5. Publish reproducible field procedures for different modems, noting protocol differences, regulatory obligations, and safe site access. Do not publish private locations, endpoints, or keys.

See [November 11 observations](../field-tests/2026-11-11-linkprobe.md). This new code was not used for those historical observations.
