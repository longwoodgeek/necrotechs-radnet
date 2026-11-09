# RF and regulatory notes — United States

**Preliminary engineering checklist, NOT a legal opinion, certification, or authorization to transmit.**

This project uses experimental 902–928 MHz LoRa hardware. Other transports, including Wi-Fi HaLow, may occupy nearby or overlapping spectrum and have their own compliance requirements.

- A licensed amateur may independently operate compliant Part 15 devices. Calling equipment "Part 15" does not establish compliance for its exact radio, firmware, antenna and mode.
- Under **47 CFR §15.247**, the frequently quoted 1 W conducted and 36 dBm EIRP figures are **conditional**. Verify certification, antenna requirements, conducted power, measured 6 dB bandwidth, power spectral density, and out-of-band emissions.
- A nominal 500 kHz LoRa bandwidth setting is **not evidence** of measured 6 dB bandwidth or Part 15 compliance.
- Under **§15.5**, Part 15 devices must accept interference and not cause harmful interference.
- Reticulum's linked/destination traffic is typically encrypted. Amateur Part 97 restrictions on messages encoded to obscure meaning require careful legal assessment; do not assume an amateur service use case is automatically permissible.
- LoRa and Wi-Fi HaLow cannot decode each other's RF signals and **could interfere** when occupying overlapping U.S. 900 MHz spectrum; evaluate channel plan and deployment.
- This project is not a public-safety dispatch system and no radio configuration has been independently certified here.

## Primary references

- [47 CFR §15.247](https://www.ecfr.gov/current/title-47/chapter-I/subchapter-A/part-15/subpart-C/section-15.247)
- [47 CFR §15.5](https://www.ecfr.gov/current/title-47/chapter-I/subchapter-A/part-15/subpart-A/section-15.5)
- [47 CFR §97.113](https://www.ecfr.gov/current/title-47/chapter-I/subchapter-D/part-97/subpart-B/section-97.113)
- [Reticulum manual](https://reticulum.network/manual/)
