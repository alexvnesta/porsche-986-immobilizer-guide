# Porsche 986/996 Immobilizer & Alarm System Guide

Reverse-engineering documentation for the Porsche 986 Boxster and 996 911 immobilizer/alarm system (M534/M535 modules).

## ⚠️ Disclaimer

For educational purposes and vehicle owners only. Verify legal ownership before any immobilizer work.

## EEPROM Map (512 bytes)

```
     0x000 ┌────────────────────────────────┐
           │  Header / Part Number          │
     0x020 ├────────────────────────────────┤
           │  Config Blocks (A & B mirror)  │
     0x080 ├────────────────────────────────┤
           │  ★ OBD FLAGS ★                 │  F6 0A = unlocked
     0x0A0 ├────────────────────────────────┤
           │  Auth / Key Sync Data          │
     0x0BA ├────────────────────────────────┤
           │  ★ TRANSPONDER IDs ★           │  for engine start
     0x100 ├────────────────────────────────┤
           │  ★ REMOTE SLOT 1 ★  (12 bytes) │  for lock/unlock
     0x10C │  ★ REMOTE SLOT 2 ★             │
     0x118 │  ★ REMOTE SLOT 3 ★             │
     0x124 │  ★ REMOTE SLOT 4 ★             │
     0x160 ├────────────────────────────────┤
           │  (unused)                      │
     0x1B0 ├────────────────────────────────┤
           │  Counter / Sync                │
     0x1EE ├────────────────────────────────┤
           │  ★ PIN CODE ★  (3 bytes)       │  key learning code
           │  ★ ECU PAIRING ★  (6 bytes)    │  links ACU↔ECU
     0x200 └────────────────────────────────┘
```

## What Do You Need To Do?

| Task | What You Need | Guide |
|------|---------------|-------|
| **Extract PIN code** | EEPROM dump | [EEPROM_MAP.md](docs/EEPROM_MAP.md) - look at offset `0x1EE` |
| **Program a remote** | Barcode from key + EEPROM access | [PROCEDURES.md](docs/PROCEDURES.md#3-programming-a-remote-via-eeprom) |
| **Program a transponder** | PIWIS/PST2 + PIN code | [PROCEDURES.md](docs/PROCEDURES.md#4-programming-a-transponder-via-piwis) |
| **Enable OBD access** | EEPROM access | [PROCEDURES.md](docs/PROCEDURES.md#6-enabling-obd-programming-access) |
| **Clone a damaged ACU** | Donor ACU + EEPROM programmer | [PROCEDURES.md](docs/PROCEDURES.md#7-cloning-a-water-damaged-acu) |
| **Analyze a dump** | Python 3 | `python3 tools/eeprom_analyzer.py your_dump.bin` |

## Quick Facts

- **ACU Location:** Under driver's seat
- **EEPROM Chip:** 93LC66 (512 bytes, SOIC-8, read in 8-bit mode)
- **Frequencies:** 315 MHz (USA) / 433 MHz (EU)
- **Keys per car:** Up to 4 transponders + 4 remotes
- **PIN stored at:** `0x1EE` (3 bytes, duplicated at `0x1F7`)

## Tools

**For EEPROM work:**
- CH341A USB programmer (~$5)
- SOIC-8 test clip (~$5)
- AsProgrammer software (free)

**For full key programming:**
- PIWIS, PST2, or ABRITES
- Blank ID48 transponder (~$5)
- Remote PCB with barcode (~$150)

## Documentation

| Document | Contents |
|----------|----------|
| [docs/EEPROM_MAP.md](docs/EEPROM_MAP.md) | Detailed memory map, byte patterns, OBD unlock data |
| [docs/PROCEDURES.md](docs/PROCEDURES.md) | Step-by-step programming guides |
| [docs/ANALYSIS.md](docs/ANALYSIS.md) | ECU/ACU pairing research |
| [docs/WIRING.md](docs/WIRING.md) | ACU connector pinout |

## Tools (Python)

```bash
# Analyze an EEPROM dump - extracts PIN, shows OBD status, remote slots
python3 tools/eeprom_analyzer.py dump.bin

# Compare two dumps (e.g., locked vs unlocked)
python3 tools/eeprom_analyzer.py dump1.bin --compare dump2.bin

# Program a remote code into a dump
python3 tools/program_remote.py original.bin modified.bin 1 <24-char-barcode>
```

## Sample Dumps

The `dumps/` folder contains sample EEPROM dumps for reference (ACU and ECU modules, locked and unlocked).

## Resources

- [bdm310/996-Immobilizer](https://github.com/bdm310/996-Immobilizer) - Original reverse engineering
- [Rennlist 996 Forum](https://rennlist.com/forums/996-forum/) - Community support
- [986 Forum](https://986forum.com) - Boxster community
- [Sportwagendoktor](https://sportwagendoktor.de) - Professional ACU repair (Germany)

## License

MIT License. Use at your own risk.

## Acknowledgments

- bdm310 for original 996-Immobilizer research
- JMG Porsche, Sportwagendoktor for technical info
- 986Forum and Rennlist communities
