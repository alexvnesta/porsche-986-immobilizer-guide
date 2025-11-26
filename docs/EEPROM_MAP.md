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

### OBD Access Control Flags (0x080-0x087)

**This controls whether the module accepts programming via OBD-II diagnostic port.**

| Offset | Locked (Default) | Unlocked | Purpose |
|--------|------------------|----------|---------|
| 0x080-0x081 | `00 00` or `55 55` | `F6 0A` | OBD enable flag 1 |
| 0x082 | `00` | `00` | Separator |
| 0x083-0x084 | `00 00` or `55 55` | `F6 0A` | OBD enable flag 2 |
| 0x085-0x087 | `55 75 00` | varies | Additional flags |

**Firmware check (pseudocode):**
```c
if (eeprom[0x80] == 0xF6 && eeprom[0x81] == 0x0A &&
    eeprom[0x83] == 0xF6 && eeprom[0x84] == 0x0A) {
    allow_obd_programming = true;
}
```

**All 3 dumps analyzed show LOCKED state:** `00 00 55 00 00 55 75 00`

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
