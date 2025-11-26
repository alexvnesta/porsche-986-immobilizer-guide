# ECU/ACU EEPROM Overlap Analysis

This document analyzes the relationship between the DME (Engine Control Unit) and ACU (Alarm Control Unit) EEPROM data.

## Summary

**Critical Finding:** The ECU and ACU share an **immobilizer secret code** that links them together. This is how the car prevents simply swapping modules.

## 2002 996 Paired Modules Analysis

### Files Analyzed
- `Eprom 93LC66A M534 ori Porsche 996 2002.bin` (ACU - 512 bytes)
- `Eprom 5P08 0261206579 ori 996 2002 ECU.bin` (ECU - 1024 bytes)

### Shared Immobilizer Secret

**ACU (0x1EE-0x1F9):**
```
0x1EE: 76 01 81   ← PIN Copy 1
0x1F1: 3D B8 7A 21 E9 94
0x1F7: 76 01 81   ← PIN Copy 2
0x1FA: 3D B8 7A 21 E9 94
```

**ECU (0x1E2-0x1EF):**
```
0x1E2: 01 02 3D B8 7A 21 E9 00 00 00 00 00 00 00 66 FD
0x1F2: 01 02 3D B8 7A 21 E9 00 00 00 00 00 00 00 66 FD
```

**Overlap: `3D B8 7A 21 E9`** - This 5-byte sequence appears in both modules!

This is the **immobilizer pairing code** that links the ECU and ACU together.

### VIN Storage

**ECU stores full VIN at 0x052:**
```
WP0CA29952S6522729
```
Decoded: WP0 (Porsche) CA2 (996 Carrera) 99 (1999?) 52 S6 522729

**ACU stores partial VIN in header (0x000-0x008):**
```
CA2.52
```
The `CA2` matches the model code from the ECU VIN.

### Part Numbers

**ECU at 0x260:**
```
1623520G9601
```
This is the Bosch part number format.

**ACU at 0x009:**
```
99 66 18 26 20 20 → 996.618.262.00 (M534 variant)
```

## 1998 ROW ECU Analysis

### File
- `ecu_1998_rest_of_world_org.bin` (ECU - 512 bytes, older format)

### VIN Storage (0x012-0x02F)
```
1495356WP0ZZZ99ZXS60372399
       └─────────────────┘
       VIN: WP0ZZZ99ZXS603723
```

The `WP0ZZZ99Z` format indicates Rest of World (ROW) market - the "ZZZ" would be replaced with region-specific codes for US/EU.

### Immobilizer Region (0x0C0-0x108)
```
000000c0: 9255 2020 2041 5300 0031 0007 4822 2cc1  .U   AS..1..H",.
000000d0: 314d b378 e03a 0f94 3d11 4492 051d 4f54  1M.x.:..=.D...OT
```

The `94 3D` sequence here may be an older format immobilizer code.

## Implications for Module Swapping

### Why You Can't Just Swap ACU/ECU

1. **Immobilizer Pairing**: The 5-byte sequence (`3D B8 7A 21 E9` in our example) must match in both ACU and ECU
2. **VIN Check**: Some modules verify VIN matches
3. **Rolling Codes**: Key sync data must be compatible

### How Shops Handle This

1. **Virgin ECU**: New ECUs come unpaired ("virgin") and learn the pairing code from ACU
2. **ABRITES/AVDI**: Can extract and transplant pairing codes
3. **Used ECU**: Requires writing new pairing code to match existing ACU

### Data to Extract Before Swapping

| From ACU | From ECU | Purpose |
|----------|----------|---------|
| PIN (0x1EE) | N/A | Programming access |
| Pairing code (0x1F1) | Pairing code (0x1E4) | Link modules |
| Transponder IDs | N/A | Key recognition |
| Remote codes | N/A | Lock/unlock |

## Dump Comparison Table

| Field | 2002 ECU | 2002 ACU | Match? |
|-------|----------|----------|--------|
| VIN | WP0CA29952S6522729 | CA2 (partial) | Partial |
| Pairing Code | 3D B8 7A 21 E9 | 3D B8 7A 21 E9 | **YES** |
| Part # Type | Bosch | Porsche | Different |

## Conclusion

The critical overlap between ECU and ACU is the **5-byte immobilizer pairing code**. This must match for the car to start. The PIN code in the ACU is separate - it controls programming access, not the immobilizer function itself.

### Key Takeaways

1. **PIN ≠ Pairing Code** - PIN (`76 01 81`) is for programming access; Pairing code (`3D B8 7A 21 E9`) links ECU↔ACU
2. **VIN in multiple places** - Full VIN in ECU, partial in ACU header
3. **Bytes after PIN are critical** - The 6 bytes at 0x1F1 and 0x1FA in ACU are the pairing code, not checksums
4. **1998 vs 2002 format differs** - Older ECUs (512 bytes) have different structure than newer ones (1024 bytes)
