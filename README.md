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

- **Transponder:** ID48 (Megamos Crypto)
- **Remote Chip:** Microchip-based (suspected Keeloq variant)
- **Frequencies:** 315 MHz (USA) or 433 MHz (EU)
- **Battery:** CR2016

## EEPROM Structure

### Memory Map (512 bytes)

| Offset | Length | Description |
|--------|--------|-------------|
| 0x000-0x008 | 9 | Header/Unknown |
| 0x009-0x00E | 6 | ACU Part Number |
| 0x00F-0x08F | 129 | Configuration Data (repeated at 0x020 and 0x050) |
| 0x090-0x0AF | 32 | Key Data Region (rolling codes, transponder sync) |
| 0x0B0-0x0FF | 80 | Transponder IDs and related data |
| 0x100-0x15F | 96 | Remote Control Slots (4 slots × 24 bytes each) |
| 0x160-0x1AF | 80 | Zeros (unused) |
| 0x1B0-0x1BF | 16 | Counter/Sync Region |
| 0x1C0-0x1ED | 46 | Zeros (unused) |
| 0x1EE-0x1F0 | 3 | **PIN/Key Learning Code (1st copy)** |
| 0x1F1-0x1F6 | 6 | Additional codes/checksums |
| 0x1F7-0x1F9 | 3 | **PIN/Key Learning Code (2nd copy)** |
| 0x1FA-0x1FF | 6 | Additional codes/checksums |

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

The 12-byte code comes from the barcode tag on new remotes (shown as 24 hex characters).

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

Some ACUs have OBD programming access disabled. ABRITES has a function called "Enable Alarm module access by OBD2" that modifies specific EEPROM bytes.

If PIWIS reports "No access authorization", you may need to:
1. Read EEPROM
2. Use ABRITES Dump Tool to modify for OBD access
3. Write modified EEPROM back
4. Retry PIWIS programming

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

## Resources

### Online References

- [bdm310/996-Immobilizer GitHub](https://github.com/bdm310/996-Immobilizer) - Original reverse engineering work
- [JMG Porsche Alarm Primer](https://www.jmgporsche.co.uk/index.php/sales-maintenance/item/234-996-986-alarm-primer) - Comprehensive technical overview
- [986 Forum](https://986forum.com) - Community support
- [Rennlist 996 Forum](https://rennlist.com/forums/996-forum/) - Community support

### Service Providers

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
│   ├── WIRING.md            # ACU connector pinout and wiring
│   └── PROCEDURES.md        # Step-by-step programming procedures
├── tools/
│   ├── eeprom_analyzer.py   # Analyze and extract codes from dumps
│   ├── program_remote.py    # Write remote codes to EEPROM
│   └── compare_dumps.py     # Compare two EEPROM dumps
└── examples/
    └── empty_slot_pattern.txt   # Reference patterns
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
