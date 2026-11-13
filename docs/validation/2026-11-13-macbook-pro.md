# MacBook Pro local validation — November 13, 2026

## Evidence and baseline

Operator: Gerry Martin / LongwoodGeek; message author label: `Longwood`.
Environment reported in the validation handoff: macOS on MacBook Pro, Python **3.14.6**, Git **2.50.1** (Apple Git-155 on the synchronization host). No macOS version or CPU architecture was recorded.

Source baseline inspected during synchronization: `85dc7d1` (merged recovered core source, PR #1). The screenshots do not record a commit SHA; this is the inspected baseline, not independently proven provenance for the original run.

Evidence: operator screenshots from the referenced “Recover SharkDeck Context” chat (10:09:45 clone, 10:12:09 boot, 10:14:03 journal, 10:15:31 tests), inspected during synchronization. Screenshots and the local database remain private and are not committed. Runtime versions are supplied by the operator/handoff and checked again during synchronization.

| Check | Recorded result |
|---|---|
| Boot | Successful; LOCAL DEVELOPMENT, EXPERIMENTAL / NOT SECURE, NOT CONNECTED |
| First SQLite message | `message.create`, author `Longwood`, local sequence `1`, no parents |
| Retrieval | Same message returned by a separate CLI process |
| Content hashes | `Local content-hash check: PASS`, twice in separate CLI processes |
| Core tests | 5 passed |
| Boot tests | 2 passed |
| LinkProbe tests | 5 passed |
| Full unittest run | 12/12, `OK`, **0.025s** |

First message body:

> RadNet Core operational. First successful boot on MacBook Pro. The Network Remembers.

Screenshot event ID: `61951e2d08454d6b21b22c926eb19442a92591c6d07be3be2fca99476cd94ace`.
With this exact first envelope in a fresh journal, the ID is reproducible. The v0.1 envelope includes local sequence and no creation timestamp; changing message fields or sequence changes the ID.

## Reproduce safely

From a clean checkout of this repository, run the following in a POSIX shell. Only the Python standard library is required. Use a new temporary journal; never reuse the operator's first journal, a station identity, a recovery volume, or a live BBS database.

```sh
python3 --version
git --version
git rev-parse HEAD
validation_dir=$(mktemp -d)
python3 -m radnet --db "$validation_dir/journal.sqlite3" boot
# Expected: no journal yet; boot must not create one.
test ! -e "$validation_dir/journal.sqlite3"
python3 -m radnet --db "$validation_dir/journal.sqlite3" post Longwood "RadNet Core operational. First successful boot on MacBook Pro. The Network Remembers."
python3 -m radnet --db "$validation_dir/journal.sqlite3" list
python3 -m radnet --db "$validation_dir/journal.sqlite3" verify
python3 -m radnet --db "$validation_dir/journal.sqlite3" verify
python3 -m radnet --db "$validation_dir/journal.sqlite3" boot
python3 -m unittest discover -s tests -v
# Remove only this disposable journal directory when finished:
rm -r -- "$validation_dir"
```

Expected: first post has author Longwood and local sequence 1; list retrieves its body/ID; both verify commands print PASS; second boot reports an existing readable journal; unittest reports 12 tests and OK. Test duration varies: **0.025s is a recorded run, not a required performance bound**. Future added tests should increase the expected count rather than be suppressed to retain 12.

The five core tests cover reopen/persistence, parent references, hash tamper detection, invalid-parent rejection, and list order. The two boot tests cover readable existing journals and absent-journal non-creation. The five LinkProbe tests cover synthetic repeatability, summary/duplicate rejection, all-loss handling, non-destructive export, and bad configuration. The export test's 2/2 ACK (100%) result is synthetic.

## Scope and limitations

This validates local software and SQLite persistence across CLI processes, not power-loss durability or production concurrency. Content hashes are not signatures, author authentication, encryption, or tamper-proof storage: a database writer can rewrite content and hashes. The author is a label, not a verified identity.

LinkProbe simulation statistics are not radio range, real delivery rates, RF throughput, route isolation, regulatory approval, or emergency reliability. Existing real-RF observations remain separately documented in the November 8 and November 11 field reports, with their original caveats. Cryptographic identity, federation, AXIS and an interactive BBS remain unimplemented in this core.

## Synchronization recheck

On November 13, the inspected clean baseline was rerun on Python 3.14.6 / Git 2.50.1: all 12 tests passed in 0.025s. The reproduction sequence above was also exercised against a disposable journal before publishing. No local SQLite databases or sidecars are included in this change; ignore rules now cover `.sqlite3` as well as `.sqlite`, `.db`, and their sidecars.
