# EEPROM Dump Collection

This folder structure is for organizing EEPROM dumps locally. **Actual .bin files are gitignored** for privacy (they contain PIN codes and other personal data).

## ACU (Alarm Control Unit) Dumps

| File | Module | Size | OBD Status | PIN | Notes |
|------|--------|------|------------|-----|-------|
| `boxster_986_m535.bin` | M535 260.07 | 512B | Locked | `DC 4E 40` | Primary reference dump |
| `996_id198_m535.bin` | M535 260.05 | 512B | Locked | `4C 02 E3` | 4 keys, 3 remotes programmed |
| `996_id201_m535.bin` | M535 260.05 | 512B | Locked | `FB 8C 40` | 2 remotes programmed |
| `2002_996_m534.bin` | M534 262.00 | 512B | Locked | `76 01 81` | Has paired ECU dump |
| `2003_996_m535_locked.bin` | M535 | 512B | Locked | `DC 6F C2` | Forum dump (locked) |
| `2003_996_m535_unlocked.bin` | M535 | 512B | **Unlocked** | `DC 6F C2` | Same module after ABRITES unlock |
| `996_m534_youtube.bin` | M534 260.06 | 512B | **Unlocked** | `D8 18 39` | M534PSI Performance video |
| `2001_986_boxster.bin` | M535 | 1439B | - | - | Raw dump (may need trimming) |
| `m534_433mhz_corrupted.bin` | M534 260.06 | 512B | - | `FF FF FF` | Corrupted - data lost |

## ECU (Engine Control Unit) Dumps

| File | Chip | Size | VIN | Notes |
|------|------|------|-----|-------|
| `1998_row_ecu.bin` | 93C66 | 512B | WP0ZZZ99ZXS603723 | Rest of World market |
| `2002_996_ecu_5p08.bin` | 5P08 | 1024B | WP0CA29952S6522729 | **Paired with 2002_996_m534.bin** |

## Key Findings

### Locked vs Unlocked Comparison
The `2003_996_m535_locked.bin` and `2003_996_m535_unlocked.bin` are the same module before/after OBD unlock. Comparing these shows exactly what ABRITES modifies.

### ECU/ACU Pairing
The `2002_996_m534.bin` ACU and `2002_996_ecu_5p08.bin` ECU are from the same car. They share a 5-byte pairing code at:
- ACU: `0x1F1` = `3D B8 7A 21 E9`
- ECU: `0x1E4` = `3D B8 7A 21 E9`

## Usage

```bash
# Extract PIN from any ACU dump
xxd -s 0x1EE -l 3 dumps/acu/boxster_986_m535.bin

# Compare locked vs unlocked
diff <(xxd dumps/acu/2003_996_m535_locked.bin) <(xxd dumps/acu/2003_996_m535_unlocked.bin)

# Extract VIN from ECU
xxd -s 0x52 -l 17 dumps/ecu/2002_996_ecu_5p08.bin
```

## Contributing

If you have additional dumps (especially paired ECU+ACU from the same vehicle), please contribute!
