# THE NETWORK REMEMBERS
## RadNet Development Diary
**NecroTechs · Gerry “LongwoodGeek” Martin + Atlas · Started retrospectively 2026-11-14**

> This is an engineering diary, not a claim that every feature is finished. Early entries are reconstructed from GitHub PRs and operator-reported tests. Future entries should be written as work occurs. Dates are UTC for GitHub events and local operator dates where stated. Quotes from the team are attributed where known; humorous console lines are not operational assertions.

### Our method
**Build → Test → Break → Fix → Document → Repeat.** Preserve originals; keep the local journal and station identity out of source control; distinguish simulation from radio evidence, configured from verified, and hash checks from signatures. Human judgment owns requirements and acceptance; AI assistance helps draft, review, debug, and document. Both can make mistakes. Screenshots, test output, commits, and field notes are the evidence.

### Nov 13, 2026 — The first archive wakes up (reconstructed)
**v0.1, PR #1** merged 14:55 UTC: recovered Python/SQLite prototype, append-only event journal, deterministic content IDs, parent references, and a read-only boot diagnostic. The earliest promise: **THE NETWORK REMEMBERS**. A content hash establishes consistency, **not** an authenticated author.

**PR #2** merged 15:20 UTC: recorded MacBook validation and added protection against accidentally committing local SQLite journals. A small but important lesson: a development repository must not become an accidental backup of private operational data.

**v0.2, PR #3** merged 17:57 UTC: local interactive terminal with classic green-phosphor presentation. This was still local-only; no public listener, authentication, federation, or emergency dispatch.

**v0.3, PR #4** merged 17:58 UTC: interactive boards, local posts and replies, parent references, pagination, and persistence. Operator acceptance included creating **General Communications**, posting **First Transmission**, restarting, and replying **“The Archive is alive!”**. The early test count reached 22 passing tests. We also encountered literal `\\n` display problems and corrected them. This is why tests and human-visible terminal inspection both matter.

### Nov 13, 2026 — The Captain's Log (reconstructed)
**v0.4, PR #5** merged 21:53 UTC: append-only Captain's Log with creation, corrections, history, search, export, provenance and uncertainty metadata. Corrections preserve originals; local timestamps and operator names are not automatically verified. On the Raspberry Pi 5, the operator reported **48/48** tests passing, then confirmed a log entry survived closing and reopening the terminal. Its title: **The Network Remembers**.

### Nov 14, 2026 — The station gets its name (reconstructed)
**v0.5, PR #6** merged 13:57 UTC: persistent local station UUID and label, read-only loading, explicit initialization, and a truthful station-status screen. Operator's station: **LGL-CyberDeck-DEV-001** on a **4 GB Raspberry Pi 5**, Debian 13 (Trixie), accessed via SSH from iPhone/iPad.

An early v0.5 test run showed **52 tests, 2 failures** around invalid station labels. After correction, **52/52 passed**. A later banner change introduced a stale assertion expecting v0.4; after updating the test, **55/55 passed**. This is not an embarrassment to erase: it demonstrates the regression suite catching mismatches between code and expectations.

The operator verified the same UUID after restarting the application, confirmed the terminal status screen, and captured green-on-black screenshots with ANSI enabled (without `--plain`). The status screen intentionally said **LOCAL / UNVERIFIED**, **Transport: NOT CONNECTED**, **Federation: NOT IMPLEMENTED**, and **Emergency dispatch: NOT AVAILABLE**. It also stated: **DRINKING PRIVILEGES: DENIED (station policy: no beverages near hardware)**. Humor is welcome; false capability claims are not.

`git status --short --ignored` showed `!!` for the station JSON, local SQLite database and WAL/SHM files, acceptance export, and Python caches: ignored, **not errors**. The operator copied the identity file to iPad/iCloud via SFTP. That establishes an off-device copy, though an independent checksum/restore verification remains desirable. The station identity is a local configuration UUID, not a cryptographic credential.

### Nov 14, 2026 — The red warning standard and v0.6 begins (current)
**Branch:** `feature/capability-evidence-v0.6`. A design note defines a capability registry and append-only evidence model: **installed ≠ configured ≠ tested ≠ currently operational**. Stale test results must not be presented as live status. LinkProbe simulation RTT must not be represented as real RF throughput.

Terminal severity design:
- **GREEN / [OK]** — normal, successful.
- **WHITE / [INFO]** — neutral information.
- **AMBER / [WARN]** — degraded, stale, or attention required.
- **RED / [ERROR], [CRITICAL]** — actual failure or urgent problem.
- Plain mode retains explicit labels; color is never the sole signal. Missing optional transport is not automatically an error.

The first implementation added `radnet/colors.py`, `tests/test_colors.py`, and red status presentation for invalid local identity. On the Pi 5, the operator's screenshot showed **61 tests in 0.132s — OK**. This validates the first color slice; it does **not** yet validate the future capability-evidence backend.

### Why we are recording this
The project is a human–AI collaboration: requirements, lived sysadmin experience, hardware, testing, and final decisions from Gerry; drafting, implementation assistance, analysis, and documentation from Atlas and other tools. The real story includes the missteps, the tests that caught them, the preservation decisions, and the occasional cat supervising development. **Pressie** was present for the v0.6 planning session and reportedly sleeping on the operator; no formal feline QA sign-off is claimed.

### Current verified boundary
**Demonstrated:** local Python BBS, message-board and Captain's Log persistence, station UUID persistence, terminal color, 61 passing tests on v0.6 branch as reported from Pi output.

**Not yet demonstrated:** real RadNet network transport, federated boards, authenticated operator identity, current radio telemetry, verified operational capability registry, emergency dispatch.

### Evidence index
- [PR #1 — core v0.1](https://github.com/longwoodgeek/necrotechs-radnet/pull/1)
- [PR #2 — validation and ignore rules](https://github.com/longwoodgeek/necrotechs-radnet/pull/2)
- [PR #3 — local terminal v0.2](https://github.com/longwoodgeek/necrotechs-radnet/pull/3)
- [PR #4 — boards v0.3](https://github.com/longwoodgeek/necrotechs-radnet/pull/4)
- [PR #5 — Captain's Log v0.4](https://github.com/longwoodgeek/necrotechs-radnet/pull/5)
- [PR #6 — station identity v0.5](https://github.com/longwoodgeek/necrotechs-radnet/pull/6)
- [v0.6 capability design](capability-evidence-v0.6.md)

### Diary entry template (for all future work)
**Date/time and time source:**  
**Version/branch/commit:**  
**Goal:**  
**What changed:**  
**Commands/tests and exact result:**  
**Evidence location (screenshot, log, PR):**  
**What failed / what we learned:**  
**Safety and preservation checks:**  
**What remains unverified:**  
**Next decision:**  

*THE NETWORK REMEMBERS.*
