# RadNet v0.5 — Station Identity and Status (work in progress)

Goal: portable local identity, truthful capability status, and headless-compatible presentation.

## Initial implemented slice
- `radnet.station.initialize(path, label)` explicitly creates a UUID-based local station identity in a separate JSON file, using exclusive creation. It never replaces an existing identity.
- `load(path)` is read-only; missing files return `None`, malformed identity raises `StationError`.
- `status(path)` distinguishes configured local identity from authenticated identity and verified connectivity.
- Unit tests cover persistence, rejection of replacement, invalid labels, corrupted data, and honest status claims.

**Not implemented yet:** CLI initialization, terminal menu integration, capability inventory, verified operational evidence, secure identities, or transport detection. No automated test execution has been claimed for this branch.

## Design constraints
- Never silently regenerate an identity after loss/corruption. Require operator-led recovery.
- A local UUID is a *record identifier*, not a public key, signature, trust anchor, or proof of identity.
- Back up identity alongside archives; restoring it to a different device is intentional and must not create simultaneous active identities without operator review.
- Configured, detected, and verified operational are separate states. Unknown is preferable to invented success.
- Do not probe radio hardware, network interfaces, keys, or emergency workflows as a side effect of reading status.
- No existing journal or Reticulum/NomadNet data is modified by this slice.

## Acceptance plan
1. Run full regression suite on Raspberry Pi 5 (Debian 13, Python 3.13.5).
2. Verify explicit identity initialization, restart persistence, and refusal to overwrite.
3. Verify missing/corrupt identity does not create a replacement.
4. Validate status never claims RF connectivity or authenticated identity without evidence.
5. Complete CLI/menu wiring and capability evidence model in later commits before requesting merge.
