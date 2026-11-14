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
