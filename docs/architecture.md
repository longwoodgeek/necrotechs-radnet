# Prototype architecture

## Tested path

~~~text
Portable computer -- USB -- Heltec V3 RNode -- ~915 MHz LoRa
                                              |
                                  obstructed/indoor radio path
                                              |
SharkDeck/WalnutPi -- USB -- LilyGo LoRa32 RNode
       |
       +-- Reticulum transport (rnsd)
       +-- NomadNet Pocket BBS
       +-- LXMF-capable endpoints and clients
~~~

The SharkDeck Wi-Fi was deliberately disabled for the reported field tests. This is an operator-reported condition; a complete route audit and nonce-based cache-exclusion test remain future work.

## Status distinctions

- **Observed:** LoRa messaging and browsing NomadNet pages across interior walls, plus operator-reported LXMF messaging at an estimated ~200 ft through building obstructions.
- **Proposed:** Proxmox/Debian VM with a dedicated USB RNode; Linux offline GNSS time via gpsd/chrony; authenticated file transfer over Reticulum using rncp; quantitative LinkProbe testing.
- **Under evaluation:** Wi-Fi HaLow (IEEE 802.11ah) as a long-range IP transport or backhaul alongside LoRa. It is a different RF waveform and **cannot directly communicate with LoRa RNodes**.
- **Concept only:** Regional FECC/SentinelLink coordination, responder authority processes, e-ink status interfaces, local resource directories, and multi-transport gateways.

## Transport neutrality

Regular 2.4 GHz Wi-Fi equipment cannot be transformed into LoRa radios through software alone. But Reticulum can route traffic over multiple appropriately configured interfaces, including suitable IP links and RNode LoRa links. This is the architectural reason to investigate HaLow separately from our low-rate LoRa layer.

## Privacy

This public overview omits station identity keys, active destinations, host serial numbers, home addresses, and private local directories. Do not publish a live radio configuration without reviewing it carefully.
