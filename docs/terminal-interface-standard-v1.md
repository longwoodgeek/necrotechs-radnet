# RadNet Terminal Interface Standard v1.0

**Status:** Adopted design standard; retroactive implementation pending verification.

## Principles
1. One presentation language across local terminal, loopback Doorbell, and future remote clients.
2. Adapt to explicit client width, not the server's terminal width. Clamp supported widths to 24–160 columns; default conservatively to 36 columns when the client width is unknown.
3. Use stacked labels and values on narrow screens; permit two-column alignment only where it fits without breaking semantic labels.
4. At nested screens, `[0]` returns exactly one level. At the top level, `[0]` disconnects. Every screen shows its current context and available actions.
5. Preserve line boundaries and sanitize untrusted content without erasing intentional structure. Never pass input to a shell.
6. Status meanings must be conveyed by words, not color alone. ANSI styling is optional; plain monochrome is first-class.
7. Avoid unbounded output; paginate and cap records and message lengths. Keep accessibility and low-bandwidth clients in scope.
8. UI refactoring must not alter event hashes, persistent journal data, SQLite schema, station identity, or write permissions.
9. Distinguish observed capability from planned or simulated capability; do not imply authenticated users, verified RF, federation, or emergency dispatch.

## Retroactive adoption checklist
- [ ] Local main menu and station status
- [ ] Message board list, posts, replies, and paging
- [ ] Captain's Log browsing, history, and editing prompts
- [ ] Capability registry and historical evidence view
- [ ] One-request Doorbell preview
- [ ] Interactive Doorbell, including nested evidence navigation
- [ ] Emergency information and resources placeholders
- [ ] Regression tests at 24, 36, 44, 80 and 120 columns
- [ ] Manual mobile SSH acceptance, plain and ANSI modes

## Rollout
Refactor shared text and navigation primitives first; migrate one screen at a time with tests. Keep the existing local and loopback interfaces working during the transition. Test each width and menu path before enabling new transports.

**Polish first. Then add.**

THE NETWORK REMEMBERS.
