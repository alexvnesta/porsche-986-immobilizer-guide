# Porsche 986/996 ACU EEPROM Memory Map

Detailed memory map for the 93LC66 EEPROM (512 bytes) in M534/M535 alarm control units.

## Quick Reference (TL;DR)

**Need to find something fast? Here are the key offsets:**

| What You Need | Offset | Size | Format |
|---------------|--------|------|--------|
| **PIN Code** | `0x1EE` | 3 bytes | `DC 4E 40` → PIN is "DC4E40" |
| **ECU Pairing Code** | `0x1F1` | 6 bytes | Links ACU↔ECU |
| **Remote Slot 1** | `0x100` | 12 bytes | From key barcode |
| **Remote Slot 2** | `0x10C` | 12 bytes | |
| **Remote Slot 3** | `0x118` | 12 bytes | |
| **Remote Slot 4** | `0x124` | 12 bytes | |
| **Part Number** | `0x009` | 6 bytes | `99 66 18 26 00 70` = 996.618.260.07 |
| **OBD Unlock Flag** | `0x080` | 2 bytes | `F6 0A` = unlocked |

**Empty remote slot looks like:** `FF FF FF FF FF FF FF FF B7 FF FF FF`

**PIN is stored twice:** at `0x1EE` and `0x1F7` (both must match)

---

## Visual Memory Map

```
0x000 ┌─────────────────────────────────────┐
      │  Header / Partial VIN               │
0x009 ├─────────────────────────────────────┤
      │  Part Number (6 bytes)              │
0x00F ├─────────────────────────────────────┤
      │  Vehicle Configuration              │
0x020 ├─────────────────────────────────────┤
      │  Config Block A                     │
0x050 ├─────────────────────────────────────┤
      │  Config Block B (mirror of A)       │
0x080 ├─────────────────────────────────────┤
      │  ★ OBD ACCESS FLAGS ★               │  ← F6 0A = unlocked
0x0A0 ├─────────────────────────────────────┤
      │  Authentication / Key Data          │
0x0BA ├─────────────────────────────────────┤
      │  ★ TRANSPONDER IDs (4 keys) ★       │  ← For engine start
0x100 ├─────────────────────────────────────┤
      │  ★ REMOTE SLOTS (4 × 12 bytes) ★    │  ← For lock/unlock
0x160 ├─────────────────────────────────────┤
      │  (unused)                           │
0x1B0 ├─────────────────────────────────────┤
      │  Counter / Sync Region              │
0x1C0 ├─────────────────────────────────────┤
      │  (unused)                           │
0x1EE ├─────────────────────────────────────┤
      │  ★ PIN CODE ★ (3 bytes)             │  ← Key learning code
0x1F1 ├─────────────────────────────────────┤
      │  ★ ECU PAIRING ★ (6 bytes)          │  ← Links ACU to ECU
0x1F7 ├─────────────────────────────────────┤
      │  PIN CODE (backup copy)             │
0x1FA ├─────────────────────────────────────┤
      │  ECU PAIRING (backup copy)          │
0x200 └─────────────────────────────────────┘
```

---

## EEPROM Chip Info

| Property | Value |
|----------|-------|
| Chip | 93LC66 (Microchip or equivalent) |
| Size | 512 bytes |
| Package | SOIC-8 |
| Read Mode | **Use 8-bit mode** |

---

## Common Tasks

### Extract PIN Code
```bash
# Using the analyzer script:
python3 tools/eeprom_analyzer.py your_dump.bin

# Manual with xxd:
xxd -s 0x1EE -l 3 -p dump.bin
```

### Check if OBD is Unlocked
Look at offset `0x080`:
- `F6 0A` = **UNLOCKED** (can program via OBD)
- `00 00` = **LOCKED** (need EEPROM access)

### Find Remote Code
Each slot is 12 bytes starting at:
- Slot 1: `0x100`
- Slot 2: `0x10C`
- Slot 3: `0x118`
- Slot 4: `0x124`

If slot shows `FF FF FF FF FF FF FF FF B7 FF FF FF`, it's empty.

---

## For More Details

- [OBD Unlock Technical Details](#obd-access-control-detailed)
- [Key Slot Structure](#key-slot-structure)
- [Byte Swapping Explained](#byte-swapping-16-bit-eeprom)
- [IPAS Codes Reference](#ipas-codes-explained)
- [Multi-Dump Analysis](#multi-dump-analysis)

---

# Technical Deep Dive

*Everything below is for those who want the full details.*

---

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
0x1F1-0x1F6    6    ★ ECU PAIRING CODE (Copy 1) ★
0x1F7-0x1F9    3    ★ PIN CODE (Copy 2) ★
0x1FA-0x1FF    6    ★ ECU PAIRING CODE (Copy 2) ★
──────────────────────────────────────────────────────────────────
```

## Part Number Decoding (0x009-0x00E)

```
Bytes:   99 66 18 26 00 70
Decoded: 996.618.260.07
         │   │   │   └── Revision (07)
         │   │   └────── Model (260)
         │   └────────── Series (618)
         └────────────── Manufacturer (996 = Porsche)
```

## OBD Access Control (Detailed)

**This controls whether the module accepts programming via OBD-II diagnostic port.**

ABRITES Commander modifies **THREE regions** (39 bytes total) to enable OBD access.

### Region 1: OBD Flags (0x080-0x08F)

| Offset | Locked | Unlocked | Purpose |
|--------|--------|----------|---------|
| 0x080-0x081 | `00 00` | `F6 0A` | OBD enable flag 1 |
| 0x083-0x084 | `55 55` | `F6 0A` | OBD enable flag 2 |

### Region 2: Authentication Values (0x0A0-0x0AF)

```
Unlocked: 00 00 8B 3B 3B 3B 3B EB 3B 3B E6 3B 64 A0 A0 3D
```

### Region 3: Additional Unlock Data (0x0B0-0x0B6)

```
Unlocked: 3D 85 E5 E5 E5 63 0C
```

### Complete OBD Unlock Patch

To unlock OBD access, write these bytes:

```
0x080: F6 0A 00 F6 0A 00 75 00 00 30 30 01 03 02 00 00
0x0A0: 00 00 8B 3B 3B 3B 3B EB 3B 3B E6 3B 64 A0 A0 3D
0x0B0: 3D 85 E5 E5 E5 63 0C
```

**These values are UNIVERSAL** - confirmed identical across multiple unlocked dumps.

## Key Slot Structure

Each key has:
1. **Transponder ID** (4 bytes) - in 0x0BA-0x0E1 region - for ENGINE START
2. **Remote Code** (12 bytes) - in 0x100+ region - for LOCK/UNLOCK

| Key | Transponder Offset | Remote Slot Offset |
|-----|-------------------|-------------------|
| 1 | 0x0BA | 0x100 |
| 2 | 0x0BF | 0x10C |
| 3 | 0x0C4 | 0x118 |
| 4 | 0x0C9 | 0x124 |

## IPAS Codes Explained

Porsche dealers access these codes via IPAS (Integrated Porsche Aftersales System):

| IPAS Code Name | Digits | EEPROM Location |
|----------------|--------|-----------------|
| **Key Learning Code (PAS-Code)** | 6 hex | `0x1EE-0x1F0` |
| **Alarm Learning Code** | 12 hex | `0x1F1-0x1F6` |
| **Remote Transmitter Code** | 24 hex | `0x100+` |

**Note:** Remote codes are NOT stored in IPAS after initial sale. Lost barcode = recover from EEPROM only.

## Byte-Swapping (16-bit EEPROM)

The 93LC66 stores 16-bit words. When writing remote codes:

```
Barcode label:    40 13 A9 89 D1 4C 23 2D BF 06 B7 C5
Write to EEPROM:  13 40 89 A9 4C D1 2D 23 06 BF C5 B7
```

Swap each pair of bytes before writing!

## Multi-Dump Analysis

Analysis of 8 ACU dumps confirms consistent structure:

| Dump | Part # | OBD Status | PIN (0x1EE) |
|------|--------|------------|-------------|
| Boxster M535 | 260.07 | LOCKED | `DC 4E 40` |
| 2003 M535 | 262.03 | LOCKED | `DC 6F C2` |
| 2003 M535 Unlocked | 262.03 | **UNLOCKED** | `DC 6F C2` |
| YouTube M534 | - | **UNLOCKED** | `D8 18 39` |

### Confirmed Universal Values

| Field | Value |
|-------|-------|
| OBD Unlock flags | `F6 0A 00 F6 0A` |
| Sync pattern | `B2 22 D4 B2 22 D4` |
| Empty slot markers | `B7` and `06` |

## ECU Pairing Code

The 6 bytes at `0x1F1` link your ACU to your ECU. They must match for the immobilizer to work:

```
ACU (0x1F1):  3D B8 7A 21 E9 94
ECU (0x1E4):  3D B8 7A 21 E9 00  ← First 5 bytes MATCH
```

**This is why you can't swap ACU or ECU modules** - the pairing must match!

## Safe vs Risky Modifications

### Safe (Tested)
- Reading PIN from 0x1EE
- Writing remote codes to 0x100+ slots
- OBD unlock (0x080 = `F6 0A`)

### Risky (Use Caution)
- Modifying transponder region (0x0B0-0x0FF)
- Changing configuration blocks
- Altering PIN values

### Always
1. Read EEPROM twice and compare
2. Keep original backup
3. Verify writes by reading back

## References

- [bdm310/996-Immobilizer](https://github.com/bdm310/996-Immobilizer) - Original reverse engineering
- [ABRITES Commander](https://www.abritus72.com/) - OBD unlock data
- [Rennlist Forums](https://rennlist.com/forums/) - Community verification
