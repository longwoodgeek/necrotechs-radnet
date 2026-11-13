# RadNet Terminal Interface v0.2 — preparation

Status: discussion handoff only. No interactive BBS, listener, transport or new command is implemented by the validation synchronization.

Start from the [validated local core](validation/2026-11-13-macbook-pro.md) and its existing `boot`, `post`, `list`, and `verify` CLI commands. Keep the NomadNet/SharkDeck BBS, identities and recovery assets separate.

Topics for the next interactive design session:

- Choose a local console first interaction and define navigation/back/quit behavior before considering remote access.
- Explore Message Boards, Station Status, Captain's Log and Resources; these are proposed menu concepts, not existing subsystems.
- Agree readable plain-text operation and an optional ANSI presentation, with a fast startup path and no animation dependency.
- Decide whether the initial session is read-only; any posting must be explicit, with a clearly selected disposable development journal and visible unverified author labels.
- Define input limits, terminal-control escaping, error handling and clean exit behavior before coding.
- Retain visible local-only/experimental status. Do not claim verified identities, radio connectivity, federation, or emergency readiness.

Proposed acceptance questions: Can a user navigate and quit without writes? Can they read existing messages without changing IDs/order semantics? If posting is in scope, does it survive reopen and retain content-hash checks? Does plain text work without color/ANSI? Are journal paths explicit and isolated? Does the existing full suite still pass?

Remote Telnet/LAN/VPN access, authentication, authorization and transport need a separate design decision; no OS shell exposure. Resume by agreeing the smallest local interaction flow, then approve its implementation scope.
