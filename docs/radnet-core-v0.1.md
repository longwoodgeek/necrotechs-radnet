# RadNet Core v0.1-dev — Milestone 1

**Experimental, local-only event journal. NOT secure messaging or production federation.**

Recovered from the November 13, 2026 RadNet boot-development source package. Python 3.10+ and SQLite; standard library only. Run from repository root.

```bash
python3 -m radnet boot
python3 -m radnet --db demo.sqlite3 post sparrow "Hello, IronGate!"
python3 -m radnet --db demo.sqlite3 list
python3 -m radnet --db demo.sqlite3 verify
python3 -m unittest discover -s tests -v
```

The database is created only at the specified path (or the default radnet-dev.sqlite3 on posting). Do not target the SharkDeck recovery filesystem or an existing BBS database.

## Implemented

- Append-only application API and local SQLite journal with WAL mode
- Deterministic SHA-256 content IDs for local event envelopes
- Parent references (not authenticated or resolved)
- CLI post/list/verify and read-only boot diagnostics
- Seven unit tests in the recovered boot-development package

## Not implemented

- Signing, verified identity, encryption, authorization, revocation, delegation
- Federation, Reticulum/LoRa transport, peer sync, delivery, custody
- Withdrawals, moderation, attachments, BBS/Telnet UI
- Verified causality, crash-safe export, robust concurrency and resource budgets

**Security:** hashes are not signatures or tamper-proof evidence. An actor with database write access can rewrite content and hashes. local_seq is local receipt order, not causality or wall-clock order. Append-only is enforced by the application API, not direct SQL.

The boot sequence intentionally reports missing cryptographic identity, federation and AXIS connector. It makes no network connection and does not create a database.

## Next milestones

1. Define stable wire envelopes separately from local sequence.
2. Design verified identities and narrow, expiring, revocable delegation (ADR-044).
3. Specify deterministic import/export, missing-parent handling, reconciliation.
4. Implement bounded Reticulum adapter, with testable offline behavior.
5. Add isolated Python Telnet terminal front end; initially LAN/VPN and read-only, never an OS shell.
6. AXIS connector pending separate protocol definition.

Keep the existing NomadNet/SharkDeck station identity and recovery assets separate from this prototype.
