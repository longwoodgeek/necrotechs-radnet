# RadNet v0.7 — Private Session Doorbell (design gate)

## Goal
Allow an invited remote operator to access RadNet without receiving a general-purpose shell or direct filesystem/database access.

## Phased approach
1. **Read-only private proof of concept:** local loopback listener, one client, bounded input/output, no shell or subprocess access. Do not open a public port.
2. **Identity and authorization:** explicit user identity distinct from station identity; least-privilege permissions; deny by default; audit connection attempts without recording secrets.
3. **Concurrency and integrity:** isolated per-client state, SQLite busy handling, transaction boundaries, reconnect and disconnect tests.
4. **Private network acceptance:** only after local tests, bind to a controlled private interface and restrict with firewall/VPN; review threat model and service privileges.
5. **Posting access:** enable only after authorization and concurrency gates pass.

## Invariants
- Existing local terminal and 75-test baseline must continue to pass.
- Preserve station identity JSON, journal and SQLite files; never commit them.
- Never claim transport, RF, federation, or emergency dispatch works until independently verified.
- No public internet exposure, guest shell, implicit user authentication, or telnet credentials.
- All connection states and failures are clearly labeled; polish before adding.

## Acceptance evidence required
Loopback connect/disconnect; malformed and oversized input; unauthorized attempt; EOF/timeout; second-client rejection in single-user mode; no shell execution; database unchanged in read-only mode; service restart; regression suite; mobile terminal readability.

## Status
Design branch opened; implementation and runtime acceptance **not yet completed**.

> Dear Diary: The SysOp says I may finally get a doorbell. Apparently I must learn not to let strangers into the server room.

## Baseline acceptance — 2026-11-14 (operator report)
- On Raspberry Pi 5, the existing **75-test** regression suite completed with **OK** after switching to the v0.7 branch.
- During an earlier local-terminal session, a complete shell command was accidentally pasted at the BBS prompt; the operator observed that RadNet did not execute it.
- This is a useful negative observation, **not** a comprehensive shell-injection or remote-session security assessment. Exact pasted bytes and complete terminal trace were not retained in this record.

## Security regression requirements arising from accidental paste
- Submit literal shell-looking input at the menu prompt and verify no OS command or subprocess is invoked.
- Include metacharacters, command substitution, oversized input, escape/control sequences, and EOF.
- Confirm malformed input cannot change station identity or append to the archive.
- Repeat against the proposed network session protocol, not only the local interactive menu.
- No test should run an actual destructive command; use mocks or harmless marker files to detect execution attempts.

## Loopback implementation acceptance — 2026-11-14 (operator screenshots)
- Added read-only, one-request TCP preview bound to `127.0.0.1`, with bounded menu input and no shell or write handlers.
- Initial 80-test run found one Linux TCP reset when rejecting oversized input. Implemented bounded draining of the remaining input; subsequent **80/80** tests passed.
- Operator launched listener in a detached tmux session and connected from a second shell to `127.0.0.1:8765`; menu selection `2` returned the expected persistent station status.
- First manually observed response flattened line breaks; updated sanitization to preserve line boundaries and added a regression test.
- Operator's latest screenshot shows **81 tests / OK**, successful second loopback request, and legible multiline station status.
- No remote-host connectivity, authentication, multiuser concurrency, or posting over the socket has been demonstrated. The listener remains loopback-only.

**Next gate:** review read-only exposure and session framing, then implement a deliberately constrained interactive loopback session with explicit connection limits and tests before any private-network binding.

## Interactive session manual acceptance — 2026-11-14
- Operator reported **85/85 automated tests OK** on Pi 5.
- Separate interactive listener on `127.0.0.1:8766` handled a single TCP connection containing menu selections `2`, `7`, then `0`.
- Screenshot confirms station status, capability registry, repeat-selection prompt, and clean `Disconnected.` response.
- **Presentation defect observed:** capability registry uses wide two-column rendering despite narrow mobile display, wrapping statuses awkwardly.
- **Navigation limitation:** `[1] VIEW CAPABILITY EVIDENCE` shown within registry is not an active nested remote menu; current remote protocol only accepts top-level selections.
- No remote-host connectivity, authenticated user access, or concurrent clients verified.

**Next polish gate:** negotiate or explicitly set client display width; support nested read-only evidence navigation without confusing top-level menu options; test and manually verify before expanding network reach.
