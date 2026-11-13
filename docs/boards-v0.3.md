# RadNet local boards v0.3 (experimental)

The local terminal supports board creation, posts, replies and pages of ten messages. Authors are **unverified**, self-entered labels. There are no accounts, authentication or authorization. Content hashes check content consistency, not identity or trust. This is local development software: no Telnet listener, remote transport, federation or emergency dispatch. Do not expose it as a public service or attach production station identities.

From the repository root:

```bash
python3 -m unittest discover -s tests -v
python3 -m radnet --db radnet-test.sqlite3 terminal --plain
```

Use the same database path on every launch to retrieve existing messages. The terminal and Station Status do not create a missing database. Opening the board browser also does not create it; explicitly creating a board or posting writes append-only events through the existing EventStore. No schema migration or database replacement is needed. Keep your SQLite journal and its sidecars private and out of Git. Do not remove or reset a journal to update the code.

Select `[1] MESSAGE BOARDS`, `[N] New board`, supply an author label and title, select the board, then `[N] New post`. Select a numbered message to read it and answer `y` to reply. `[>]` and `[<]` page through messages; `[0]` returns. Replies preserve their parent event ID but appear in the same chronological list, not a threaded tree. Legacy CLI `message.create` events remain in the journal; the interactive board browser displays `board.message` events only.

Inputs are limited to 100 characters for board/post titles, 32 for authors and 4000 for bodies; there are up to 100 boards. Control characters are rejected or sanitized for display. These input/page limits are **not a total resource bound**: current views scan the local journal, so memory and latency grow with it. Captain's Log, resources and network directory remain placeholders.

## Validation and presentation regression

On November 13, 2026 the operator reported **22/22 tests passing on the MacBook**, created General Communications, posted First Transmission, restarted the BBS and retrieved it, then replied “The Archive is alive!” successfully. This is operator-reported local persistence evidence, not remote/radio validation.

The follow-up presentation patch replaces literal backslash-n separators in board lists, post lists, message headings and interruption output. The startup banner now says v0.3, local posting enabled and authors unverified; Station Status and CLI help describe the same capabilities. Four new regression tests bring the suite to **26 tests**. They exercise startup/status/help, console newlines, interruption without database creation, and a two-session create/post/reopen/reply workflow using temporary journals. These follow-up checks were executed in a separate development checkout; they are not a claim that the operator has rerun the patched interface on the MacBook.

The v0.2 read-only terminal was introduced by PR #3; PR #4 adds the local writing flow described here. See [the historical v0.2 guide](terminal-v0.2.md).
