# NecroTechs RadNet

**Project home:** https://github.com/longwoodgeek/necrotechs-radnet

**Open experiments in resilient, low-bandwidth communication, digital preservation, and offline-first design.**

> **Status: experimental maker project.** Not an emergency service, a certified radio product, or a guarantee of communications availability.

RadNet is an evolving NecroTechs project investigating how small, inexpensive devices can exchange messages and serve useful local information without a conventional internet connection. Our current working prototype combines [Reticulum](https://reticulum.network/), [LXMF](https://github.com/markqvist/LXMF), [RNode](https://unsigned.io/rnode/), and [NomadNet](https://github.com/markqvist/NomadNet).

**What we've demonstrated (operator-observed, November 2026):**

- Two-way Reticulum/LXMF connectivity between a portable laptop + Heltec V3 RNode and a SharkDeck/WalnutPi + LilyGo RNode, using approximately 915 MHz LoRa.
- Successful browsing of NomadNet Pocket BBS content over radio in indoor tests through one and then two walls.
- Operator-reported message delivery at an estimated **~200 ft / ~61 m** with an apartment building and HVAC obstacles between stations; not a surveyed distance or statistically measured reliability result.
- An operational, Wi-Fi-isolated radio/BBS host during the initial field tests (its wall clock was **not synchronized**, and is not valid for RTT claims).

**What has NOT been demonstrated:** measured application throughput or packet-delivery rates; measured peer RSSI/SNR; guaranteed range; independent FCC compliance certification; emergency-service reliability; fully validated infrastructure failover.

## Start here

| Topic | Document |
|---|---|
| How the prototype fits together | [Architecture](docs/architecture.md) |
| Reproducible observations and caveats | [Field tests](docs/field-tests/2026-11-08-radio-tests.md) |
| Current incident and recovery | [Operation Phoenix](docs/recovery/operation-phoenix-2026-11-09.md) |
| Roadmap and proposed tools | [Roadmap](docs/roadmap.md) |
| Radio/regulatory caution | [Radio safety notes](docs/radio-and-regulatory-notes.md) |
| Values, attribution and AI transparency | [Engineering charter](docs/engineering-charter.md) |
| Contributing and reporting vulnerabilities | [CONTRIBUTING](CONTRIBUTING.md) · [SECURITY](SECURITY.md) |

## Design priorities

1. **Transport neutrality:** use networks that are actually available—radio, LAN, or other Reticulum-compatible media—without conflating a message's transport with endorsement of its contents.
2. **Preservation first:** protect identities, logs, and source material; retain raw evidence privately and publish accurate, reviewed summaries.
3. **No fabricated benchmarks:** report configured rates as configured rates; capture measured throughput, latency and delivery only after actual tests.
4. **Human-controlled emergency workflows:** no automated process should claim emergency authority without explicit, accountable policies and safeguards.
5. **Accessibility and cost:** favor repairability, low-cost proven hardware, readable local interfaces, and low-energy field operation.

## Project status

- **RadNet field node and BBS:** prototype demonstrated; a later SD-card filesystem incident required preservation and repair (see recovery log).
- **LinkProbe:** Python prototype drafted and offline codec/summary unit tests reported; *not yet validated on physical radio interfaces*. Public release will follow a code/security review and hardware verification.
- **FECC/SentinelLink:** design-stage concepts; no certified or deployed regional emergency service.
- **GNSS/offline time:** proposed, not yet installed or proven on the SharkDeck host.

## Independent projects and acknowledgments

Reticulum, LXMF, RNode, NomadNet, and third-party hardware are independent projects; NecroTechs does not claim authorship or affiliation. See their own documentation and licenses.

RadNet project engineering and observations are led by Gerry Martin / LongwoodGeek, with openly acknowledged AI-assisted research, drafting and development. All field observations and real-world decisions require human verification.

## License

Documentation and original example code in this launch kit are made available under the [MIT License](LICENSE), unless separately noted. Third-party projects retain their own licenses.