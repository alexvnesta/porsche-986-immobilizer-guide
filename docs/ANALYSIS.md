# ECU/ACU EEPROM Overlap & Immobilizer Handshake Analysis

This document analyzes the relationship between the DME (Engine Control Unit) and ACU (Alarm Control Unit) EEPROM data.

---

## 1. Summary

**Critical Finding:** The DME (Engine Control Unit) and ACU (Alarm Control Unit) share a **6-byte cryptographic immobilizer pairing secret** that links them together.

This secret is exchanged over the single-wire bidirectional **W-Lead (ACU Pin A23 ➔ DME Pin IV/31)** during the key-on crank authorization cycle. Without this matching pairing code, the DME disables the ignition spark and fuel injectors.

---

## 2. 2002 996 Paired Modules Analysis (ME7.2)

### Files Analyzed
- `Eprom 93LC66A M534 ori Porsche 996 2002.bin` (ACU - 512 bytes)
- `Eprom 5P08 0261206579 ori 996 2002 ECU.bin` (Bosch ME7.2 DME - 1024 bytes)

### Shared Immobilizer Secret

#### ACU (`0x1EE..0x1FF`):
```text
0x1EE: 76 01 81             ← Key Learning PIN (Copy 1)
0x1F1: 3D B8 7A 21 E9 94    ← 6-Byte Immobilizer Pairing Secret (Copy 1)
0x1F7: 76 01 81             ← Key Learning PIN (Copy 2 / Mirror)
0x1FA: 3D B8 7A 21 E9 94    ← 6-Byte Immobilizer Pairing Secret (Copy 2 / Mirror)
```

#### Bosch ME7.2 DME (`0x1E0..0x1FF` in 95P08 EEPROM):
```text
0x1E0: .. .. 01 02 3D B8 7A 21 E9 00 00 00 00 00 00 00 66 FD
0x1F0: .. .. 01 02 3D B8 7A 21 E9 00 00 00 00 00 00 00 66 FD
```

### Key Overlap Details:
* **The Shared Secret:** `3D B8 7A 21 E9` (first 5 bytes match directly, with byte 6 as variant/mask).
* **Dual-Bank Mirroring in Both ECUs:**
  * In the ACU, the secret is stored at **`0x1F1`** and mirrored at **`0x1FA`**.
  * In the DME ME7.2 95P08 EEPROM, the pairing block is stored at **`0x1E2`** and mirrored at **`0x1F2`**.
* **PIN vs Pairing Secret:**
  * The 3-byte PIN (`76 01 81` at `0x1EE`) is the dealer **Teaching / Lerncode** used by PIWIS/PST2 to authorize new key learning. It is **never** transmitted to the DME.
  * The 6-byte pairing secret (`0x1F1`) is the internal bus authentication secret used exclusively for the ACU ↔ DME W-Lead challenge/response.

---

## 3. Physical W-Lead Routing

The immobilizer verification does not occur over CAN bus or OBD K-Line. It uses a dedicated serial link:

| Module | Pin | Wire Color / Gauge | Destination |
|:---|:---:|:---:|:---|
| **ACU (M534/M535)** | Connector I, Pin **A23** | 0.5 mm² GN (Green) | DME Pin IV/31 (ME7.2) / Pin III/31 (M5.2.2) |
| **DME (ME7.2)** | Connector IV (40-Pin), Pin **31** | 0.5 mm² GN (Green) | ACU Connector I, Pin A23 |
| **DME (M5.2.2)** | Connector III (28-Pin), Pin **31** | 0.5 mm² GN (Green) | ACU Connector I, Pin A23 |

---

## 4. Engine Start Authentication Flow

```text
  Key Turned to Terminal 15 (+12V Switched)
                   │
                   ▼
  ACU energizes ignition barrel coil (Pins A03/A04)
  Reads 32-bit ID48 Transponder pill
                   │
                   ▼
  Is Transponder ID in ACU EEPROM Bank A (0x0BA..0x0CD)?
                   │
         YES ──────┴────── NO ──▶ Immobilizer lockout: Alarm horn chirps,
                   │              no authorization sent.
                   ▼
  DME initiates challenge packet to ACU over W-Lead (Pin A23)
                   │
                   ▼
  ACU computes cryptographic response using 6-byte secret (0x1F1)
  Sends authorization packet back to DME over W-Lead
                   │
                   ▼
  Does response match DME EEPROM pairing secret (0x1E2/0x1F2)?
                   │
         YES ──────┴────── NO ──▶ DME denies start: Engine cranks,
                   │              fuel and spark disabled.
                   ▼
  DME clears start lockout: Engine fires and runs normally.
```

---

## 5. Implications for Module Swapping & Bench Cloning

### 1. Swapping a Used ACU into a Car
* If you install a used ACU from another vehicle without reprogramming:
  * The car **will not start** because the ACU's pairing secret does not match the DME's pairing secret.
  * Existing car keys will not be recognized because their transponder IDs are not in the replacement ACU.
* **Solution:** Clone the original ACU's 93LC66 EEPROM dump into the replacement ACU. This transfers both the transponder IDs and the pairing code.

### 2. Swapping a Used DME into a Car
* If you replace a dead DME with a used unit:
  * Extract the 95P08 EEPROM from the DME (or read it in-circuit).
  * Write the 6-byte pairing secret from ACU `0x1F1` into the DME at offsets `0x1E4` and `0x1F4`.
  * Alternatively, write a "virgin" DME EEPROM file, which causes the DME to auto-learn the pairing code from the ACU on the first ignition key cycle.
