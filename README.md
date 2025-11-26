# Porsche 986/996 Immobilizer & Alarm System Guide

A comprehensive reverse-engineering guide for the Porsche 986 Boxster and 996 911 immobilizer/alarm system (M534/M535 modules). This documentation covers EEPROM structure, key programming, remote coding, and DIY repair procedures.

## ⚠️ Disclaimer

This information is provided for educational purposes and for owners working on their own vehicles. Always verify you have legal ownership before attempting any immobilizer work. Improper modifications can leave your vehicle inoperable.

## Table of Contents

- [Overview](#overview)
- [Hardware](#hardware)
- [EEPROM Structure](#eeprom-structure)
- [Key Codes & Locations](#key-codes--locations)
- [Programming Procedures](#programming-procedures)
- [Tools Required](#tools-required)
- [Troubleshooting](#troubleshooting)
- [Resources](#resources)

## Overview

### System Components

The Porsche 986/996 immobilizer system consists of:

| Component | Location | Function |
|-----------|----------|----------|
| **ACU (Alarm Control Unit)** | Under driver's seat | Central locking, immobilizer, alarm, windows, convertible top |
| **DME (Engine Control Unit)** | Engine bay | Engine management, communicates with ACU |
| **Key Fob** | N/A | Contains transponder (ID48) and RF remote transmitter |
| **Antenna** | Around ignition barrel | Reads transponder chip |

### Module Versions

| Part Number | Version | Frequency | Market |
|-------------|---------|-----------|--------|
| 996.618.260.0x | M535 | 315 MHz | USA |
| 996.618.260.0x | M534 | 433 MHz | EU/ROW |
| 996.618.262.0x | M535/M534 | 315/433 MHz | Post-2001 (different wiring) |

**Important:** Pre-2001 and post-2001 modules have different wiring and are NOT directly interchangeable.

### Key Components

Each key contains TWO separate systems:

1. **Transponder (ID48/Megamos chip)** - RFID chip that allows the car to START
2. **Remote Transmitter** - RF transmitter for lock/unlock/trunk functions

These are programmed separately and require different codes.

## Hardware

### ACU Board

- **Main Processor:** M37710 (Mitsubishi 16-bit microcontroller)
- **EEPROM:** 93LC66 (512 bytes, SOIC-8 package)
- **Interface:** Microwire/SPI (NOT I2C)

### EEPROM Access

The 93LC66 can be read/written in-circuit using a SOIC-8 clip:

```
Programmer: CH341A (or TL866, XProg, etc.)
Software: AsProgrammer, NeoProgrammer, or similar
Chip: 93C66 (select 8-bit mode, 512 bytes)
```

**Tip:** Ground the main processor's oscillator pin while reading/writing to prevent interference.

### Key Fob Hardware

- **Transponder:** ID48 (Megamos Crypto) - glass pill component
- **Remote Board:** 4 generations (P1, P2, P3, P4) across production years
- **Frequencies:** 315 MHz (USA/Japan) or 433.92 MHz (EU/ROW)
- **Battery:** CR2016
- **Rolling Code:** Encrypted, ~40 button presses max before desync

### Key Slot Allocation

The M534/M535 has **4 total slots** for keys:
- Factory default: 3 transponder slots + 2 remote slots (2 remote keys + 1 workshop key)
- Maximum: 4 of each (transponder and remote)
- Each remote has its own code card (required for programming radio module, NOT transponder)
- Ignition lock has a separate code card with TRW identifier
- **Exception:** M531 (early Boxster) has central locking but NO remote function

### Comfort Functions

When using the remote:
- **Hold open button** while unlocking → lowers both side windows
- **Hold close button** while locking → raises both side windows
- **Seat memory** (if equipped): Driver seat moves to saved position on unlock (3 positions available)

**Seat Memory Troubleshooting:**
| Symptom | Likely Cause |
|---------|--------------|
| Seat goes to wrong position | Radio modules swapped between keys |
| Seat always moves fully forward | Radio module signal degraded - check module & ACU |

## EEPROM Structure

### Memory Map (512 bytes)

| Offset | Length | Description |
|--------|--------|-------------|
| 0x000-0x008 | 9 | Header (may contain partial VIN) |
| 0x009-0x00E | 6 | ACU Part Number |
| 0x00F-0x01F | 17 | Vehicle configuration |
| 0x020-0x04F | 48 | **Configuration Block A** |
| 0x050-0x07F | 48 | **Configuration Block B** (mirror of A) |
| 0x080-0x09F | 32 | **OBD Access Control Flags (CRITICAL)** |
| 0x0A0-0x0B9 | 26 | Key sync/authentication data |
| 0x0BA-0x0E1 | 40 | **Transponder IDs (4 keys × ~10 bytes, with redundancy)** |
| 0x0E2-0x0FF | 30 | **Radio Codes - Copy 1 (Keys A, B partial)** |
| 0x100-0x13B | 60 | **Radio Codes - Primary (Keys B, C, D)** |
| 0x13C-0x15F | 36 | **Radio Codes - Copy 2 (Keys C, D) + markers** |
| 0x160-0x1AF | 80 | Zeros (unused) |
| 0x1B0-0x1BF | 16 | Counter/Sync Region (B2 22 D4 pattern) |
| 0x1C0-0x1ED | 46 | Zeros (unused) |
| 0x1EE-0x1F0 | 3 | **PIN/Key Learning Code (1st copy)** |
| 0x1F1-0x1F6 | 6 | Additional codes/checksums |
| 0x1F7-0x1F9 | 3 | **PIN/Key Learning Code (2nd copy)** |
| 0x1FA-0x1FF | 6 | Additional codes/checksums |

### Key Slot Structure

The ACU stores data for **4 keys (A, B, C, D)**. Each key has:
1. **Transponder ID** (4 bytes) - stored in 0x0BA-0x0E1 region
2. **Radio Code** (4 bytes minimum) - stored **twice** for redundancy

| Key | Transponder ID Offset | Radio Code Copy 1 | Radio Code Copy 2 |
|-----|----------------------|-------------------|-------------------|
| A | 0x0BA-0x0BD | 0x0E2-0x0E5 | 0x0F7-0x0FA |
| B | 0x0BF-0x0C2 | 0x100-0x103 | 0x115-0x118 |
| C | 0x0C4-0x0C7 | 0x11E-0x121 | 0x133-0x136 |
| D | 0x0C9-0x0CC | 0x13C-0x13F | 0x151-0x154 |

**Example - Fully programmed module (3 keys + 1 empty):**
```
Key A Transponder: 25 69 A1 08 (at 0x0BA)  |  Radio: 40 01 4B F8
Key B Transponder: 94 9A 5F 02 (at 0x0BF)  |  Radio: 40 01 4F 13
Key C Transponder: 16 ED 60 03 (at 0x0C4)  |  Radio: 40 16 C2 9A
Key D Transponder: CE 56 E9 1D (at 0x0C9)  |  Radio: FF FF FF FF (EMPTY)
```

*Note: The key slot structure above is based on community reverse engineering of a fully-programmed module.
The annotated hex dump below shows a different module with mostly empty slots.*

### Annotated Hex Dump

Below is an actual 986 Boxster ACU EEPROM dump (512 bytes) with critical regions labeled.

> **Color Key:** 🟦 Part Number | 🟥 OBD Flags | 🟩 Transponder IDs | 🟨 Remote Slots | 🟪 PIN Code | 🟫 ECU Pairing

<!--
Note: GitHub markdown doesn't render colors in code blocks. The dump below uses
ASCII art and emoji markers. For a colored view, see the HTML version in docs/.
-->

```
╔═══════════════════════════════════════════════════════════════════════════════╗
║                          HEADER & PART NUMBER                                 ║
╚═══════════════════════════════════════════════════════════════════════════════╝
             🟦 Part Number: 996.618.260.07
             ▼▼▼▼▼▼▼▼▼▼▼▼▼
00000000: 0000 0000 0000 0000 00 99 6618 2600 70 00  ..........f.&.p.
                                ▲▲ ▲▲▲▲ ▲▲▲▲ ▲▲
                                99.66.18.26.00.70

╔═══════════════════════════════════════════════════════════════════════════════╗
║                    CONFIGURATION BLOCK 1 (0x010-0x04F)                        ║
╚═══════════════════════════════════════════════════════════════════════════════╝
00000010: 0000 0037 11f4 f1c0 0400 0000 0000 0000  ...7............
00000020: 77ff 9000 4ba0 bea1 cfff 1e05 0f00 0d0d  w...K...........
00000030: 0d02 0d20 020d a010 0716 2040 2725 03ff  ... ...... @'%..
00000040: ed08 000a 0000 0000 0000 0000 0000 0000  ................

╔═══════════════════════════════════════════════════════════════════════════════╗
║                  CONFIGURATION BLOCK 2 - MIRROR (0x050-0x07F)                 ║
║                        (Must match Block 1 exactly)                           ║
╚═══════════════════════════════════════════════════════════════════════════════╝
00000050: 77ff 9000 4ba0 bea1 cfff 1e05 0f00 0d0d  w...K...........
00000060: 0d02 0d20 020d a010 0716 2040 2725 03ff  ... ...... @'%..
00000070: ed08 000a 0000 0000 0000 0000 0000 0000  ................

╔═══════════════════════════════════════════════════════════════════════════════╗
║  🟥🟥🟥  OBD ACCESS CONTROL FLAGS (0x080-0x09F)  🟥🟥🟥                        ║
║         Controls whether OBD-II programming is allowed                        ║
╚═══════════════════════════════════════════════════════════════════════════════╝
          🟥 OBD Flag 1     🟥 OBD Flag 2
          ▼▼▼▼▼▼            ▼▼▼▼▼▼▼
00000080: 0000 55 00 0055 75 00 0030 3007 0101 0000  ..U..Uu..00.....
          ▲▲▲▲▲▲    ▲▲▲▲▲▲▲
          LOCKED    LOCKED (needs F6 0A 00 F6 0A 00 75 to unlock)

00000090: 3a81 05ad 2d82 2f87 3101 3c83 030a 0c09  :...-./.1.<.....
000000a0: 3d0a 7677 7674 0474 742a 7777 7777 7777  =.vwvt.tt*wwwwww

╔═══════════════════════════════════════════════════════════════════════════════╗
║  🟩🟩🟩  TRANSPONDER IDs & KEY DATA (0x0B0-0x0E1)  🟩🟩🟩                      ║
║              ID48 chip identifiers for programmed keys                        ║
╚═══════════════════════════════════════════════════════════════════════════════╝
                                    🟩 Transponder ID
                                    ▼▼▼▼▼▼▼▼▼▼▼
000000b0: 7777 7777 7777 30c0 2f00 944c 1072 bfff  wwwwww0./..L.r..
                                    ▲▲▲▲▲▲▲▲▲▲▲
                                    ID: 94 4C 10 72 (Key A)

000000c0: ffff ff78 ffff ffff 78ff ffff ff78 944c  ...x....x....x.L
000000d0: 1072 bfff ffff ff78 ffff ffff 78ff ffff  .r.....x....x...
          ▲▲▲▲
          Same ID (redundant copy)

000000e0: ff78 ffff ffff ffff ffff b7ff ffff ffff  .x..............
000000f0: 06ff ffff ffff 06ff ffff ffff ffff ffb7  ................

╔═══════════════════════════════════════════════════════════════════════════════╗
║  🟨🟨🟨  REMOTE CONTROL SLOTS (0x100-0x15F)  🟨🟨🟨                            ║
║                         ALL SLOTS EMPTY                                       ║
║           FF bytes with B7/06 markers = UNPROGRAMMED                          ║
╚═══════════════════════════════════════════════════════════════════════════════╝
          ┌─── Remote Slot A (EMPTY) ───────────────────────────────────┐
00000100: ffff ffff ffff ffff b7 ff ffff ffff 06 ff  ................
00000110: ffff ffff 06 ff ffff ffff ffff ff b7 ffff  ................
          └─── Remote Slot B (EMPTY) ───────────────────────────────────┘
00000120: ffff ffff ffff b7 ff ffff ffff 06 ff ffff  ................
00000130: ffff 06 ff ffff ffff ffff ff b7 ffff ffff  ................
          └─── Remote Slot C (EMPTY) ───────────────────────────────────┘
00000140: ffff ffff b7 ff ffff ffff 06 ff ffff ffff  ................
00000150: 06 ff ffff ffff ffff ff b7 0000 0000 0000  ................
          └─── Remote Slot D (EMPTY) ──┘
          ▲                        ▲
          Empty marker             Empty marker
          (always 06)              (always B7)

╔═══════════════════════════════════════════════════════════════════════════════╗
║                         UNUSED REGION (0x160-0x1AF)                           ║
╚═══════════════════════════════════════════════════════════════════════════════╝
00000160: 0000 0000 0000 0000 0000 0000 0000 0000  ................
00000170: 0000 0000 0000 0000 0000 0000 0000 0000  ................
00000180: 0000 0000 0000 0000 0000 0000 0000 0000  ................
00000190: 0000 0000 0000 0000 0000 0000 0000 0000  ................
000001a0: 0000 0000 0000 0000 0000 0000 0000 0000  ................

╔═══════════════════════════════════════════════════════════════════════════════╗
║                     COUNTER / SYNC REGION (0x1B0-0x1BF)                       ║
╚═══════════════════════════════════════════════════════════════════════════════╝
                        Rolling code sync pattern
                        ▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼
000001b0: 0000 0000 00 b2 22d4 b222 d4 31 a600 0000  ......"..".1....
                       ▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲
                       B2 22 D4 B2 22 D4 (always this pattern)

╔═══════════════════════════════════════════════════════════════════════════════╗
║                         UNUSED REGION (0x1C0-0x1ED)                           ║
╚═══════════════════════════════════════════════════════════════════════════════╝
000001c0: 0000 0000 0000 0000 0000 0000 0000 0000  ................
000001d0: 0000 0000 0000 0000 0000 0000 0000 0000  ................

╔═══════════════════════════════════════════════════════════════════════════════╗
║  🟪🟪🟪  PIN / KEY LEARNING CODES (0x1EE-0x1FF)  🟪🟪🟪                        ║
║              CRITICAL - Required for all programming                          ║
╚═══════════════════════════════════════════════════════════════════════════════╝
                                          🟪 PIN Code starts here
                                          ▼▼▼▼▼▼
000001e0: 0000 0000 0000 0000 0000 0000 0000 dc4e  ...............N
                                               ▲▲▲▲
                                               PIN byte 1-2: DC 4E

          🟪 PIN Copy 1    🟫 ECU Pairing Code    🟪 PIN Copy 2    🟫 ECU Pairing
          ▼▼▼▼▼▼▼▼        ▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼     ▼▼▼▼▼▼▼▼        ▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼
000001f0: 40 6d 32d0 56d9 78 dc 4e40 6d 32d0 56d9 78  @m2.V.x.N@m2.V.x
          ▲▲                 ▲▲▲▲▲▲
          PIN byte 3: 40     PIN bytes 1-3: DC 4E 40
          (at 0x1F0)         (repeat at 0x1F7-0x1F9)

┌─────────────────────────────────────────────────────────────────────────────────────────┐
│  LEGEND (this dump)                                                                     │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│  🟪 PIN CODE:        DC 4E 40  (3 bytes at 0x1EE & 0x1F7, stored twice)                 │
│  🟫 ECU PAIRING:     6D 32 D0 56 D9 78  (links ACU to DME/ECU - don't modify!)          │
│  🟦 PART NUMBER:     996.618.260.07  (decoded from 99 66 18 26 00 70)                   │
│  🟥 OBD FLAGS:       00 00 55 00 00 55 75  (LOCKED - needs F6 0A to unlock)             │
│  🟩 TRANSPONDER:     94 4C 10 72  (1 key programmed)                                    │
│  🟨 REMOTE SLOTS:    All empty (FF with B7/06 markers)                                  │
│     SYNC PATTERN:    B2 22 D4  (rolling code synchronization)                           │
│     EMPTY MARKERS:   B7 and 06 bytes indicate unprogrammed slots                        │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

### Byte-Swapping (16-bit EEPROM)

The 93LC66 is a **16-bit organized** EEPROM. Each memory address holds a 16-bit word (2 bytes). When dumped byte-by-byte, the order depends on how the programmer reads it out:

```
How Porsche stores data:    [High Byte][Low Byte]
How raw dump appears:       [Low Byte][High Byte]
```

**To read codes correctly, swap each adjacent byte pair:**

| Data Type | Raw Dump | Byte-Swapped (Correct) |
|-----------|----------|------------------------|
| PIN Code | `D8 18 87 39...` | `18 D8 39 87...` → PIN is `18 D8 87` |
| Remote Code | `13 40 89 A9 4C D1...` | `40 13 A9 89 D1 4C...` |

**When to swap:**

| Operation | Swap Needed? | Reason |
|-----------|--------------|--------|
| Read PIN/remote codes | **Yes** - swap to read | See human-readable values |
| Write new remote code | **Yes** - swap before writing | Module expects swapped format |
| Write unlock flag (`F6 0A`) | **No** | It's a known raw constant |

**Example: Writing a new remote code**

If your remote barcode reads `40 13 A9 89 D1 4C 23 2D BF 06 B7 C5`, write this to the raw dump:

```
Barcode (human-readable):  40 13 A9 89 D1 4C 23 2D BF 06 B7 C5
Write to EEPROM (swapped):  13 40 89 A9 4C D1 2D 23 06 BF C5 B7
```

### Part Number Decoding (0x009-0x00E)

```
Example: 99 66 18 26 00 70
Decoded: 996.618.260.07
```

### PIN/Key Learning Code (0x1EE and 0x1F7)

The 3-byte PIN code is stored twice for redundancy:

```
Location 1: 0x1EE, 0x1EF, 0x1F0
Location 2: 0x1F7, 0x1F8, 0x1F9

Example: DC 4E 40
```

This code is required for ALL programming operations via PIWIS/PST2/ABRITES.

### Remote Control Slots (0x100-0x15F)

Each remote slot is 12 bytes. Up to 4 remotes can be programmed.

**Empty/Unprogrammed Pattern:**
```
0100: FF FF FF FF FF FF FF FF B7 FF FF FF FF FF 06 FF
```
The `B7` and `06` bytes are markers in the unprogrammed state.

**Programmed Remote Example:**
```
0100: 40 05 90 50 23 6E 31 7F 29 18 D8 21 A3 5F EE 19
      |<-------- 12-byte remote code -------->| |extra|
```

The 12-byte code comes from the barcode label on new remote PCBs:

```
Remote Part Number: 996.637.244.17
Barcode: *40 17 52 3C D1 7E A3 A3 19 2A 27 E4*
          |<------ 12 bytes (24 hex chars) ------>|
```

Additional label fields: IND (index), FKW (production date), LNR (serial), ID

### Counter/Sync Region (0x1B0)

```
01B0: 00 00 00 00 00 B2 22 D4 B2 22 D4 31 A6 00 00 00
                     |<-- sync pattern -->|
```

The `B2 22 D4` pattern appears to be rolling code synchronization data.

## Key Codes & Locations

### Summary of All Codes

| Code | Length | EEPROM Location | Purpose |
|------|--------|-----------------|---------|
| PIN/Key Learning Code | 3 bytes | 0x1EE, 0x1F7 | Enter programming mode |
| Remote Code | 12 bytes | 0x100+ | Program remote lock/unlock |
| Transponder ID | 4 bytes | 0x0C0 area | Identify key for starting |
| Immobilizer Code | 8 bytes | Varies | Teach new ACU to car |
| Part Number | 6 bytes | 0x009 | Identify module version |

### IPAS Codes (from Porsche dealer)

Porsche stores these codes in their IPAS database, accessible by VIN:

- **Key Learning Code** - Same as PIN in EEPROM
- **Remote Transmitter Codes** - For each original key's remote
- **DME Programming Code** - For ECU work
- **Alarm Learning Code** - For ACU replacement

**Note:** Remote codes are NOT stored in IPAS after initial sale. If you lose the barcode tag, the code is unrecoverable without special equipment.

## Programming Procedures

### Option 1: Direct EEPROM Modification (No PIWIS needed for remotes)

**For Remote Programming:**

1. Read EEPROM from ACU using CH341A + SOIC-8 clip
2. Get the 12-byte code from your new remote's barcode tag
3. Write the code to offset 0x100 (slot 1)
4. Flash modified EEPROM back to ACU
5. Test remote functionality

```bash
# Using the provided Python script:
python3 program_remote.py original.bin modified.bin 1 400590502366E317F2918D821
```

### Option 2: PIWIS/PST2 Programming

**For Transponder Programming:**

1. Connect PIWIS via OBD-II port
2. Navigate to: Diagnostics → Boxster 986 → Alarm → Maintenance/Repair → Teach Keys
3. Enter 3-byte PIN (e.g., `DC 4E 40`)
4. Insert key with new transponder in ignition
5. Select position (1-4)
6. Press "Learn"

**For Remote Programming (requires barcode):**

1. Connect PIWIS via OBD-II port
2. Navigate to: Diagnostics → Boxster 986 → Alarm → Maintenance/Repair → Teach Remote Control
3. Enter 3-byte PIN
4. Enter 12-byte remote code from barcode (24 characters)
5. Select position (1-4)
6. Press "Learn"

### Option 3: ABRITES/AVDI

ABRITES can:
- Extract PIN from EEPROM dump
- Enable OBD programming access
- Program transponders and remotes
- Calculate codes from dumps

### Enabling OBD Programming Access

Some ACUs have OBD programming access disabled. This is an anti-theft feature - even with the correct PIN, the module refuses programming commands over OBD-II.

#### OBD Unlock - Full Picture

ABRITES Commander modifies **THREE regions** to enable OBD access, not just the flags:

| Region | Offset | Bytes Changed |
|--------|--------|---------------|
| OBD Flags | 0x080-0x08F | 16 bytes |
| Auth Bypass | 0x0A0-0x0AF | 16 bytes |
| Unlock Data | 0x0B0-0x0B6 | 7 bytes |

#### Region 1: OBD Flags (0x080-0x08F)

```
Locked:   00 00 00 55 55 00 50 75 30 50 03 30 00 05 00 00
Unlocked: F6 0A 00 F6 0A 00 75 00 00 30 30 01 03 02 00 00
          ^^ ^^ ^^ ^^ ^^    ^^    ^^ ^^ ^^ ^^    ^^
```

The `F6 0A` magic number at 0x080 and 0x083 is the primary enable flag.

#### Region 2: Authentication Bypass (0x0A0-0x0AF)

```
Locked:   00 00 7A 7A 75 7A 75 73 75 75 7A 7A 00 00 00 00
Unlocked: 00 00 8B 3B 3B 3B 3B EB 3B 3B E6 3B 64 A0 A0 3D
```

#### Region 3: Additional Unlock (0x0B0-0x0B6)

```
Locked:   00 00 00 00 00 00 4C
Unlocked: 3D 85 E5 E5 E5 63 0C
```

#### Universal Unlock Patch (CONFIRMED)

Analysis of multiple unlocks confirms the values are **UNIVERSAL**, not per-module:

```
0x080: F6 0A 00 F6 0A 00 75 00 00 30 30 01 03 02 00 00
0x090: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
0x0A0: 00 00 8B 3B 3B 3B 3B EB 3B 3B E6 3B 64 A0 A0 3D
0x0B0: 3D 85 E5 E5 E5 63 0C
```

These exact bytes work across different modules (verified from ABRITES output and community unlocks).

*Data sources: ABRITES Commander For Porsche 4.1, Digital Kaos forum*

#### Why This Exists

This is an anti-theft measure. If someone steals your car and plugs in a diagnostic tool, they cannot simply program a new key - the module refuses. Physical access to the EEPROM is required to enable service mode first.

## Tools Required

### Minimum for EEPROM Work

- CH341A USB programmer (~$5)
- SOIC-8 test clip (~$5)
- AsProgrammer or NeoProgrammer software (free)
- Hex editor (HxD, etc.)

### For Full Key Programming

- PIWIS, PST2, or ABRITES AVDI
- Blank ID48 transponder chips (~$2-10)
- New remote PCB with barcode (~$120-150)

### Optional but Helpful

- Multimeter
- Soldering equipment (if SOIC clip doesn't work)
- Second ACU for testing

## Troubleshooting

### Remote Not Working After Programming

1. **Check frequency** - USA uses 315 MHz, EU uses 433 MHz
2. **Verify code entry** - Must be exactly 12 bytes (24 hex chars)
3. **Try resyncing** - Press remote button 2-3 times near car
4. **Check antenna wiring** - Pins 1 and 22 on ACU connector

### PIWIS Reports "No Access Authorization"

1. OBD programming access may be disabled
2. Use ABRITES to enable OBD access
3. Or modify EEPROM directly (see ABRITES dump tool documentation)

### Car Won't Start After ACU Work

1. Verify EEPROM was written correctly (read back and compare)
2. Check PIN locations (0x1EE and 0x1F7) match
3. Ensure transponder data wasn't corrupted
4. May need to re-teach transponder via PIWIS

### Rolling Code Out of Sync

The 986/996 uses a challenge-response rolling code system. If remote gets too far out of sync (~40 button presses), it cannot be recovered without reprogramming.

### Resynchronization vs Reprogramming

**These are NOT the same thing!**

| Operation | What It Does | When to Use |
|-----------|--------------|-------------|
| **Resync** | Re-introduces an already-paired radio module to ACU | Remote temporarily out of sync |
| **Reprogram** | Registers NEW transponder + radio module with code card | New key, or module replacement |

**Critical Warning:** Resynchronizing a radio module **without first testing its signal** is strongly discouraged. The ACU may permanently disable the radio module if the signal is faulty.

The transponder and radio module are stored as a **single unit** in each key slot. If the pairing is incorrect (e.g., modules swapped between keys), resync will fail.

### Remote Locked Out (Play Protection)

If you press the remote buttons rapidly many times, the system locks out for ~60 seconds as an anti-tampering measure. Wait and try again.

### Remote LED Diagnostics

| LED Behavior | Meaning |
|--------------|---------|
| Rapid continuous blink | Normal operation |
| Rhythmic 2-3 pulses on button press | Normal |
| Slow blink (~1/sec) | **Processor failure - irreversible** |
| LED stays on with ignition | System defect |

### Power-Saving Mode (No Remote Response)

After ~120 hours (5 days) without ignition activation, the ACU disables the RF receiver to save battery. The remote won't work but mechanical key entry still functions. **Fix:** Turn ignition key to re-enable receiver.

### Horn Beeps When Locking

| Beeps | Meaning |
|-------|---------|
| 1 honk | A monitored component is open (door, hood, glovebox, center console) |
| 2 honks | ACU malfunction |

### All Keys Stop Working (Transponder)

If NO keys start the car (not just remote, but turning ignition), this indicates ACU failure - the transponder recognition circuit has failed. Requires ACU repair or replacement.

## Common ACU Failures (Repairable)

The M534/M535 alarm control units can develop various faults, most of which are repairable:

| Symptom | Likely Cause |
|---------|--------------|
| **No PIWIS connection (W-Line/K-Line)** | Communication circuit failure - car won't start, transponder not recognized |
| **One/both doors won't lock/unlock** | Central locking driver circuit failure |
| **Door immediately reopens after locking** | Latch sensor or driver circuit issue |
| **Fuel filler flap won't open/close** | Fuel flap circuit failure |
| **Alarm horn doesn't sound** | Horn driver circuit failure |
| **Turn signals don't flash on lock/unlock** | Indicator circuit failure |
| **Seat always moves fully forward on unlock** | Radio module signal degraded or ACU memory corruption |
| **ACU never enters sleep mode (battery drain)** | Power management circuit failure (should sleep after ~120 hours) |
| **ACU incorrectly coded** | Software/EEPROM configuration issue |

### ACU Location

The alarm control unit (M531/M534/M535) is located **under the driver's seat** in the 986 and 996.

### Water Damage

Common cause of ACU failure is water intrusion from:
- Convertible top seal leaks (986 Boxster)
- Clogged drain channels
- A/C condensation

Water causes corrosion on the PCB, leading to the failures listed above.

## Resources

### Online References

- [bdm310/996-Immobilizer GitHub](https://github.com/bdm310/996-Immobilizer) - **Original reverse engineering work** (PIN locations, part number decoding, hardware details)
- [Sportwagendoktor FAQ (German)](https://sportwagendoktor.de/faq/faq-porsche-986-996-980/) - Excellent technical FAQ on keys, alarm modules, and programming
- [JMG Porsche Alarm Primer](https://www.jmgporsche.co.uk/index.php/sales-maintenance/item/234-996-986-alarm-primer) - Comprehensive technical overview
- [Digital Kaos Forum](https://www.digital-kaos.co.uk/forums/) - Locksmith community, OBD unlock help
- [MHH Auto Forum](https://mhhauto.com/) - EEPROM dumps and immo discussions
- [RennTech.org](https://www.renntech.org/) - Porsche technical community
- [Rennlist 996 Forum](https://rennlist.com/forums/996-forum/) - Community support
- [986 Forum](https://986forum.com) - Boxster community support

### Service Providers

- **Sportwagendoktor (Germany)** - ACU repair, frequency conversion, key programming
- **JMG Porsche (UK)** - Remote programming, ACU repair, code extraction
- **ECU Doctors (USA)** - ACU exchange, remote sales with barcodes
- **FobFix (UK)** - Remote refurbishment, barcode recreation

### Parts Sources

- **Diamond Key Supply** - New remotes with barcodes (~$410)
- **ECU Doctors** - New remotes with code cards (~$150-200)
- **Amazon/eBay** - Blank ID48 transponders (~$5-10)

## File Structure

```
├── README.md                 # This file
├── docs/
│   ├── EEPROM_MAP.md        # Detailed EEPROM memory map
│   ├── ANALYSIS.md          # ECU/ACU pairing code analysis
│   ├── WIRING.md            # ACU connector pinout and wiring
│   └── PROCEDURES.md        # Step-by-step programming procedures
├── tools/
│   ├── eeprom_analyzer.py   # Analyze and extract codes from dumps
│   └── program_remote.py    # Write remote codes to EEPROM
├── dumps/                   # Sample EEPROM dumps (ACU & ECU)
│   ├── acu/                 # Alarm Control Unit dumps
│   └── ecu/                 # Engine Control Unit dumps
└── examples/
    └── reference_patterns.txt   # Reference patterns
```

## Contributing

Contributions welcome! If you discover additional EEPROM structure details, please submit a PR or open an issue.

## License

This documentation is provided under the MIT License. Use at your own risk.

## Acknowledgments

- bdm310 for the original 996-Immobilizer reverse engineering
- JMG Porsche for technical documentation
- The 986Forum and Rennlist communities
- Various MHH Auto forum contributors
