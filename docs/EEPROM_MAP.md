# Porsche 986/996 ACU EEPROM Memory Map

Detailed memory map for the 93LC66 EEPROM (512 bytes) in M534/M535 alarm control units.

## EEPROM Chip Specifications

| Property | Value |
|----------|-------|
| Chip | 93LC66 (Microchip or equivalent) |
| Size | 512 bytes (4096 bits) |
| Package | SOIC-8 |
| Interface | Microwire/SPI (NOT I2C) |
| Organization | 256 x 16-bit or 512 x 8-bit |
| Read Mode | Use 8-bit mode for this application |

## Complete Memory Map

### Header Region (0x000-0x00F)

```
Offset  Length  Description
------  ------  -----------
0x000   9       Unknown/Header data
0x009   6       ACU Part Number (see decoding below)
0x00F   1       Unknown
```

**Part Number Decoding:**
```
Bytes at 0x009-0x00E: 99 66 18 26 00 70
                      │  │  │  │  │  │
                      │  │  │  │  │  └─ Minor revision (07)
                      │  │  │  │  └──── Major revision (0)
                      │  │  │  └─────── Model code (26)
                      │  │  └────────── Series (18)
                      │  └───────────── Product (66)
                      └────────────────  Manufacturer (99=Porsche)

Decoded: 996.618.260.07
```

### Configuration Data (0x010-0x08F)

```
Offset  Length  Description
------  ------  -----------
0x010   4       Unknown configuration
0x014   12      Unknown
0x020   48      Configuration block 1 (repeated at 0x050)
0x050   48      Configuration block 2 (mirror of 0x020)
0x080   16      Vehicle configuration flags
```

The configuration blocks at 0x020 and 0x050 contain identical data - likely for redundancy.

### Key Data Region (0x090-0x0AF)

```
Offset  Length  Description
------  ------  -----------
0x090   16      Rolling code counters and sync data
0x0A0   16      Additional key pairing data
```

This region contains dynamic data that changes as keys are used.

### Transponder Region (0x0B0-0x0FF)

```
Offset  Length  Description
------  ------  -----------
0x0B0   16      Transponder configuration
0x0C0   16      Transponder ID slots (4 bytes each, up to 4 transponders)
0x0D0   16      Additional transponder data
0x0E0   16      Transponder sync/counter data
0x0F0   16      Unknown (often contains markers B7, 06)
```

**Transponder ID Location:**
Each transponder (ID48 chip) has a unique 4-byte ID stored in this region.

### Remote Control Slots (0x100-0x15F)

This is the most important region for remote programming.

```
Offset    Length  Description
------    ------  -----------
0x100-0x10B  12   Remote Slot 1 (12-byte code from barcode)
0x10C-0x10F   4   Slot 1 extra data (counter/checksum?)
0x110-0x11B  12   Remote Slot 2
0x11C-0x11F   4   Slot 2 extra data
0x120-0x12B  12   Remote Slot 3
0x12C-0x12F   4   Slot 3 extra data
0x130-0x13B  12   Remote Slot 4
0x13C-0x13F   4   Slot 4 extra data
0x140-0x15F  32   Additional remote data/unused
```

**Empty Slot Pattern:**
```
FF FF FF FF FF FF FF FF B7 FF FF FF FF FF 06 FF
```
The `B7` at offset +8 and `06` at offset +14 are markers for unprogrammed state.

**Programmed Slot Example:**
```
40 05 90 50 23 6E 31 7F 29 18 D8 21 A3 5F EE 19
│<──────── 12-byte barcode code ────────>│ │extra│
```

### Unused Region (0x160-0x1AF)

```
Offset  Length  Description
------  ------  -----------
0x160   80      All zeros (unused/reserved)
```

### Counter/Sync Region (0x1B0-0x1BF)

```
Offset  Length  Description
------  ------  -----------
0x1B0   5       Zeros
0x1B5   6       Sync pattern (e.g., B2 22 D4 B2 22 D4)
0x1BB   2       Counter value
0x1BD   3       Zeros
```

The `B2 22 D4` pattern is related to rolling code synchronization.

### Unused Region (0x1C0-0x1ED)

```
Offset  Length  Description
------  ------  -----------
0x1C0   46      All zeros (unused/reserved)
```

### PIN/Key Learning Code Region (0x1EE-0x1FF)

**This is the most critical region for programming access.**

```
Offset  Length  Description
------  ------  -----------
0x1EE   3       PIN Code (1st copy) - KEY LEARNING CODE
0x1F1   6       Additional codes (checksum, immobilizer?)
0x1F7   3       PIN Code (2nd copy) - Redundant copy
0x1FA   6       Additional codes (mirrors 0x1F1?)
```

**PIN Code Format:**
```
Location 0x1EE: DC 4E 40  ─┐
                          ├─ These should match
Location 0x1F7: DC 4E 40  ─┘

Enter in PIWIS as: DC 4E 40 (3 bytes, 6 hex characters)
```

## Hex Dump Examples

### Empty/Virgin ACU (Remote Slots)

```
0100: FF FF FF FF FF FF FF FF B7 FF FF FF FF FF 06 FF  ................
0110: FF FF FF FF 06 FF FF FF FF FF FF FF FF B7 FF FF  ................
0120: FF FF FF FF FF FF B7 FF FF FF FF FF 06 FF FF FF  ................
0130: FF FF 06 FF FF FF FF FF FF FF FF B7 FF FF FF FF  ................
```

### Programmed ACU (With 2 Remotes)

```
0100: 40 05 90 50 23 6E 31 7F 29 18 D8 21 A3 5F EE 19  @..P#n1.)..!._..
0110: 64 37 23 7D AD 40 05 90 50 23 6E 31 7F 29 40 17  d7#}.@..P#n1.)@.
0120: F7 55 5C 29 23 47 1B 1C 76 A3 B4 58 C0 1A 11 B8  .U\)#G..v..X....
0130: AA 7E F6 40 17 F7 55 5C 29 23 47 1B FF FF FF FF  .~.@..U\)#G.....
```

### PIN Region Comparison

**Example 1:**
```
01E0: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 DC 4E  ...............N
01F0: 40 6D 32 D0 56 D9 78 DC 4E 40 6D 32 D0 56 D9 78  @m2.V.x.N@m2.V.x
                          ^^^^^^^^
                          PIN repeated at 0x1F7
```

**Example 2 (from video):**
```
01E0: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 D8 18  ...............
01F0: 39 87 73 31 64 A6 18 DF 87 D8 31 39 A6 73 DF 64  9.s1d.....19.s.d
```

## Byte-Swapping Notes

The ABRITES software has a "Swap Bytes L/H" function because the 93LC66 can be read in 16-bit mode where bytes are swapped. When reading in **8-bit mode** (recommended), no swapping is needed.

If your dump looks scrambled, try:
1. Re-read in 8-bit mode
2. Or swap every pair of bytes

## Checksum Information

There may be checksums in the EEPROM, but they haven't been fully documented. Known observations:

- The PIN is stored twice (0x1EE and 0x1F7) for redundancy
- Configuration blocks at 0x020 and 0x050 are mirrors
- Modifying remote codes at 0x100 appears to work without updating checksums

## Modifying the EEPROM

### Safe Modifications

These modifications are known to work:

1. **Writing remote codes to 0x100-0x10B** - Tested and working
2. **Reading PIN from 0x1EE** - Confirmed accurate

### Potentially Unsafe Modifications

These should be done with caution:

1. Modifying transponder region (0x0B0-0x0FF)
2. Changing configuration blocks (0x020, 0x050)
3. Altering PIN values

### Always Keep Backups!

Before any modification:
1. Read EEPROM at least twice
2. Compare both reads to verify consistency
3. Save original file in a safe location
4. Verify write by reading back and comparing
