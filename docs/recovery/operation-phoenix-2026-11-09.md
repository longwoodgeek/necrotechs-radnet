# Operation Phoenix — SharkDeck ext4 recovery

**Date:** 2026-11-09  
**Status:** Raw full-disk backup **complete**; filesystem repair and successful reboot **not yet verified**.

## Incident

After an apparent overnight power cable failure and unplanned shutdown, the SharkDeck's root ext4 filesystem became mounted read-only. Writing a new directory failed. Inspection identified `/dev/mmcblk0p2` as root. Kernel logs showed an aborted ext4 journal, failed CRC metadata checks, filesystem I/O errors and a protective read-only remount. The boot command line requested read-write; this was not an intentional readonly configuration.

The uncontrolled power loss is a plausible cause, but the evidence does not independently rule out storage-hardware problems.

## Sector-by-sector preservation

The station was safely shut down, and the nominal 256 GB SD card was imaged via a Mac SD-card reader using **GNU ddrescue** with a recovery map.

| Reported quantity | Result |
|---|---|
| SD card size | **250,277,265,408 bytes** |
| Image rescue | **100.00%** |
| Read errors | **0** |
| Bad sectors | **0 bytes** |
| Bad areas | **0** |
| ddrescue | **Finished** |

An initial raw-device sizing problem on macOS caused a bogus petabyte-scale remaining-data display; the transfer was resumed using the **same map** with `--size=250277265408`.

The image includes the **corrupted** filesystem state. A successful read of all sectors is **not proof of healthy ext4 metadata or reliable flash storage**. The disk image and private Reticulum identities were **not uploaded to GitHub**.

## Planned recovery

1. Confirm image file length against source capacity.
2. Replace/verify power cable and supply.
3. Preserve the image as a recovery master. Due to limited free storage, the original card is a possible offline repair candidate; a replacement card is preferable when available.
4. Inspect and repair the ext4 root partition only **while unmounted**, using appropriate Linux filesystem tools.
5. Verify writable root, surviving identities, Reticulum transport, NomadNet pages, and services before continuing radio experiments.

**Preservation rule:** Image first. Repair second. Validate third.
