# Porsche 986/996 ACU EEPROM Memory Map

Detailed memory map for the 93LC66 EEPROM (512 bytes) in M534/M535 alarm control units.

## EEPROM Chip Specifications

| Property | Value |
|----------|-------|
| Chip | 93LC66 (Microchip or equivalent) |
| Size | 512 bytes (4096 bits) |
| Package | SOIC-8 |
| Interface | Microwire/SPI (NOT I2C) |
| Organization | 256 × 16-bit words |
| Read Mode | Use 8-bit mode (512 bytes) |

## Complete Memory Map

```
Offset      Size    Description
──────────────────────────────────────────────────────────────────
0x000-0x008    9    Header (may contain partial VIN)
0x009-0x00E    6    ACU Part Number
0x00F-0x01F   17    Vehicle configuration

0x020-0x04F   48    Configuration Block A
0x050-0x07F   48    Configuration Block B (MIRROR of A)

0x080-0x087    8    ★ OBD ACCESS CONTROL FLAGS ★
0x088-0x09F   24    Additional flags / rolling code data

0x0A0-0x0B9   26    Key sync/authentication data
0x0BA-0x0E1   40    ★ TRANSPONDER IDs (4 keys × ~10 bytes) ★
0x0E2-0x0FF   30    Radio codes region 1 (Keys A partial)

0x100-0x15F   96    ★ REMOTE CONTROL CODES (4 slots) ★

0x160-0x1AF   80    Unused (zeros)

0x1B0-0x1B4    5    Zeros
0x1B5-0x1BA    6    Sync pattern (B2 22 D4 repeated)
0x1BB-0x1BF    5    Counter values

0x1C0-0x1ED   46    Unused (zeros)

0x1EE-0x1F0    3    ★ PIN CODE (Copy 1) ★
0x1F1-0x1F6    6    Checksums / additional codes
0x1F7-0x1F9    3    ★ PIN CODE (Copy 2) ★
0x1FA-0x1FF    6    Checksums / additional codes
──────────────────────────────────────────────────────────────────
```

## Critical Regions Detailed

### Part Number (0x009-0x00E)

```
Bytes:   99 66 18 26 00 70
Decoded: 996.618.260.07
         │   │   │   └── Revision (07)
         │   │   └────── Model (260)
         │   └────────── Series (618)
         └────────────── Manufacturer (996 = Porsche)
```

### OBD Access Control (0x080-0x0B6)

**This controls whether the module accepts programming via OBD-II diagnostic port.**

ABRITES Commander modifies **THREE regions** to enable OBD access - not just the flags!

#### Region 1: OBD Flags (0x080-0x08F)

```
         0  1  2  3  4  5  6  7  8  9  A  B  C  D  E  F
Locked:   00 00 00 55 55 00 50 75 30 50 03 30 00 05 00 00
Unlocked: F6 0A 00 F6 0A 00 75 00 00 30 30 01 03 02 00 00
          ^^^^^^^^^^^^^^^^^^    ^^    ^^ ^^ ^^    ^^
```

| Offset | Locked | Unlocked | Purpose |
|--------|--------|----------|---------|
| 0x080-0x081 | `00 00` | `F6 0A` | OBD enable flag 1 |
| 0x083-0x084 | `55 55` | `F6 0A` | OBD enable flag 2 |
| 0x086 | `50` | `75` | Access mode |
| 0x088-0x08B | `30 50 03 30` | `00 30 30 01` | Config flags |
| 0x08D | `05` | `02` | Unknown flag |

#### Region 2: Authentication Values (0x0A0-0x0AF)

```
         0  1  2  3  4  5  6  7  8  9  A  B  C  D  E  F
Locked:   00 00 7A 7A 75 7A 75 73 75 75 7A 7A 00 00 00 00
Unlocked: 00 00 8B 3B 3B 3B 3B EB 3B 3B E6 3B 64 A0 A0 3D
                ^^^^^^^^^^^^^^^^^^^^^^^^^^^^ ^^^^^^^^^^^
```

These bytes appear to be authentication/challenge-response bypass values.

#### Region 3: Additional Unlock Data (0x0B0-0x0B6)

```
         0  1  2  3  4  5  6
Locked:   00 00 00 00 00 00 4C
Unlocked: 3D 85 E5 E5 E5 63 0C
          ^^^^^^^^^^^^^^^^^^^^
```

Note: Bytes 0x0B7+ (transponder IDs) are NOT modified.

#### Complete OBD Unlock Patch

To unlock OBD access, modify these 33 bytes:

```
0x080: F6 0A 00 F6 0A 00 75 00 00 30 30 01 03 02 00 00
0x0A0: 00 00 8B 3B 3B 3B 3B EB 3B 3B E6 3B 64 A0 A0 3D
0x0B0: 3D 85 E5 E5 E5 63 0C
```

**WARNING:** The 0x0A0 and 0x0B0 values shown above may be module-specific.
The `F6 0A` flags at 0x080 are consistent, but the authentication bypass
values might need to be calculated per-module by ABRITES.

*Data source: ABRITES Commander For Porsche 4.1 (www.abritus72.com)*

### Key Slot Structure (0x0BA-0x154)

Each key has:
1. **Transponder ID** (4 bytes) - in 0x0BA-0x0E1 region
2. **Radio Code** (4+ bytes) - stored TWICE for redundancy

| Key | Transponder Offset | Radio Copy 1 | Radio Copy 2 |
|-----|-------------------|--------------|--------------|
| A | 0x0BA-0x0BD | 0x0E2-0x0E5 | 0x0F7-0x0FA |
| B | 0x0BF-0x0C2 | 0x100-0x103 | 0x115-0x118 |
| C | 0x0C4-0x0C7 | 0x11E-0x121 | 0x133-0x136 |
| D | 0x0C9-0x0CC | 0x13C-0x13F | 0x151-0x154 |

**Verified against PIWIS diagnostic output - transponder IDs match exactly.**

### Remote Control Slots (0x100-0x15F)

Each slot is approximately 24 bytes with the 12-byte barcode code at the start.

**Empty slot pattern:**
```
FF FF FF FF FF FF FF FF B7 FF FF FF FF FF 06 FF
                        ^^              ^^
                        Empty markers (B7 and 06)
```

**Programmed slot example:**
```
40 01 4F 13 06 1E 41 5F C6 04 0F AE ...
└─────────┘
Radio code (first 4 bytes visible on barcode as 8 hex chars)
```

### PIN Code Region (0x1EE-0x1FF)

The 3-byte PIN is stored **twice** for redundancy:

```
0x1EE: [PIN byte 1] [PIN byte 2] [PIN byte 3]
0x1F7: [PIN byte 1] [PIN byte 2] [PIN byte 3]  ← Must match!
```

**Examples from analyzed dumps:**

| Dump | PIN at 0x1EE | PIN at 0x1F7 | Match |
|------|--------------|--------------|-------|
| Boxster | `DC 4E 40` | `DC 4E 40` | ✓ |
| Car (ID 198) | `4C 02 E3` | `4C 02 E3` | ✓ |
| Junkyard (ID 201) | `FB 8C 40` | `FB 8C 40` | ✓ |

### Sync Pattern (0x1B5-0x1BA)

All analyzed dumps show: `B2 22 D4 B2 22 D4`

This pattern is related to rolling code synchronization.

## Byte-Swapping (16-bit EEPROM)

The 93LC66 stores 16-bit words. Depending on how you read the dump, bytes may appear swapped:

```
EEPROM stores:  [High Byte][Low Byte]
Raw 8-bit dump: [Low Byte][High Byte]  ← each pair reversed
```

**When to swap:**

| Operation | Swap Needed? | Notes |
|-----------|--------------|-------|
| Read PIN code | Yes | To see human-readable value |
| Read radio code | Yes | To match barcode label |
| Write radio code | Yes | Swap before writing to EEPROM |
| Write OBD unlock (`F6 0A`) | No | Raw constant, no interpretation |

**Example:**
```
Barcode label:    40 13 A9 89 D1 4C 23 2D BF 06 B7 C5
Write to EEPROM:  13 40 89 A9 4C D1 2D 23 06 BF C5 B7
```

## Multi-Dump Comparison

Analysis of 4 different EEPROM sources confirms consistent structure:

| Field | Boxster | Car (198) | Junkyard (201) | Verified |
|-------|---------|-----------|----------------|----------|
| Part # offset | 0x009 | 0x009 | 0x009 | ✓ |
| Config mirror | 0x020=0x050 | 0x020=0x050 | 0x020=0x050 | ✓ |
| OBD flags | 0x080 | 0x080 | 0x080 | ✓ |
| PIN offset | 0x1EE & 0x1F7 | 0x1EE & 0x1F7 | 0x1EE & 0x1F7 | ✓ |
| Sync pattern | 0x1B5 | 0x1B5 | 0x1B5 | ✓ |
| Remote slots | 0x100+ | 0x100+ | 0x100+ | ✓ |

**All dumps show identical structure - offsets are consistent across modules.**

## Safe vs Risky Modifications

### Safe (Tested)
- Reading PIN from 0x1EE
- Writing remote codes to 0x100+ slots
- Reading transponder IDs
- OBD unlock (0x080 = `F6 0A 00 F6 0A`)

### Risky (Use Caution)
- Modifying transponder region (0x0B0-0x0FF)
- Changing configuration blocks (0x020, 0x050)
- Altering PIN values (could lock out all access)

### Always
1. Read EEPROM twice and compare
2. Keep original backup in safe location
3. Verify writes by reading back

## Multi-Dump Analysis (8 ACU + 2 ECU dumps)

### ACU Dump Summary

| Dump | Part # | OBD Status | PIN (0x1EE) | Notes |
|------|--------|------------|-------------|-------|
| Your Boxster | 260.07 | LOCKED | `DC 4E 40` | Empty remote slots |
| Car ID 198 | 260.05 | LOCKED | `4C 02 E3` | 4 keys, 3 remotes |
| Junkyard ID 201 | 260.05 | LOCKED | `FB 8C 40` | 2 remotes |
| 2003 M535 | - | LOCKED | `DC 6F C2` | Forum dump |
| 2003 M535 Unlocked | - | **UNLOCKED** | `DC 6F C2` | Forum unlock |
| M534 433MHz | 260.06 | CORRUPT | `FF FF FF` | Data lost |
| M534 2002 | 262.00 | LOCKED | `76 01 81` | Has header VIN |
| YouTube M534 | 260.06 | **UNLOCKED** | `D8 18 39` | Already unlocked |

### ECU Dump Summary

| Dump | Size | VIN | Notes |
|------|------|-----|-------|
| 1998 ROW | 512 bytes | WP0ZZZ99ZXS603723 | Rest of World |
| 2002 996 | 1024 bytes (5P08) | WP0CA29952S622729 | USA Carrera |

ECU dumps contain full VIN at different offsets than ACU dumps.

### Confirmed Universal Values

| Field | Value | Verified Across |
|-------|-------|-----------------|
| OBD Unlock flags | `F6 0A 00 F6 0A` | 3 unlocked dumps |
| Auth bypass (0x0A2) | `8B 3B 3B 3B 3B EB 3B 3B E6 3B 64 A0 A0 3D` | 3 unlocked dumps |
| Unlock data (0x0B0) | `3D 85 E5 E5 E5 63 0C` | 3 unlocked dumps |
| Sync pattern | `B2 22 D4 B2 22 D4` | All valid dumps |
| Empty markers | `B7` and `06` | All dumps |

## Known Unknowns

Areas that are not fully understood yet:

### Header Region (0x000-0x008)
```
Boxster:    00 00 00 00 00 00 00 00 00  (empty)
Car 198:    41 41 32 99 39 58 09 80 E3  ("AA2" visible)
Junkyard:   43 41 32 98 58 57 09 82 A4  ("CA2" visible)
```
- Some modules have ASCII characters that could be partial VIN
- Your Boxster has all zeros - unclear if this matters
- **Need:** More samples to determine pattern

### Bytes After PIN (0x1F1-0x1F6 / 0x1FA-0x1FF)
```
Boxster:    6D 32 D0 56 D9 78
Car 198:    00 CD 3A D9 7C 99
Junkyard:   63 50 EB A3 C8 8D
```
- These 6 bytes after each PIN copy differ per module
- Could be: checksums, immobilizer secret, DME pairing code
- They repeat (0x1F1 = 0x1FA pattern)
- **Need:** Determine if these are calculated or independent

### Counter Values (0x1BB-0x1BC)
```
Boxster:    31 A6
Car 198:    7D 87
Junkyard:   19 B2
```
- Follows the `B2 22 D4` sync pattern
- Different on each module
- **Need:** Before/after dump to see what increments these

### ~~OBD Unlock Authentication (0x0A0-0x0B6)~~ RESOLVED
Confirmed **UNIVERSAL** - same values work across different modules:

| Source | 0x0A2-0x0AF | 0x0B0-0x0B6 |
|--------|-------------|-------------|
| ABRITES | `8B 3B 3B 3B 3B EB 3B 3B E6 3B 64 A0 A0 3D` | `3D 85 E5 E5 E5 63 0C` |
| Forum unlock | `8B 3B 3B 3B 3B EB 3B 3B E6 3B 64 A0 A0 3D` | `3D 85 E5 E5 E5 63 0C` |

**IDENTICAL!** The unlock patch is fixed, not per-module calculated.

### ~~Radio Code Full Length~~ RESOLVED
Barcode confirmed to show **12 bytes (24 hex characters)**:
```
40 17 52 3C D1 7E A3 A3 19 2A 27 E4
```
From label on new remote PCB (996.637.244.17)

### Checksums
- No obvious checksum algorithm identified
- Remote code modifications work without updating other bytes
- Configuration blocks mirror each other (0x020 = 0x050)
- **Need:** Test if arbitrary modifications cause rejection
