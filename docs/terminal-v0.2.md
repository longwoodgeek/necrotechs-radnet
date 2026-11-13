# RadNet local terminal v0.2 (historical)

This guide describes the original v0.2 milestone. For the current terminal with local posting, see [local boards v0.3](boards-v0.3.md). The read-only session guarantee below does not apply to explicit board creation, posts or replies in v0.3.

The first interactive BBS shell is **local, read-only and offline**. It has no Telnet listener, authentication, federation, Reticulum transport, or emergency dispatch. It never invokes a system shell. The guest interface reads existing SQLite journals in read-only mode and does not create a database.

From repository root:

```bash
python3 -m radnet --db radnet-test.sqlite3 terminal
python3 -m unittest discover -s tests -v
```

The menu provides Message Boards (existing local `message.create` events), Station Status, Captain's Log placeholder, Community Resources placeholder, Network Directory placeholder, Emergency Information safety notice, and Disconnect.

The `--plain` option suppresses ANSI color for terminals that don't support it. The startup is intentionally fast; cinematic animations are deferred until they can be disabled and do not misrepresent component status.

## Security and correctness

- Read-only SQLite connection uses URI `mode=ro`; a missing database is not created.
- Author fields in the local journal are unverified. Content hashes do not authenticate the author.
- Displayed messages are truncated and flattened to reduce terminal control injection risk.
- Do not expose this prototype over public Telnet or connect it to production station identities.
- The emergency page explicitly states the interface cannot request or dispatch assistance.

Next: add proper terminal output sanitization, pagination and board structure; then design an isolated, bounded network adapter with tests and operator opt-in.
