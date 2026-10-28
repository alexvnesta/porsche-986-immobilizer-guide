# Porsche 986/996 ACU EEPROM Memory Map

Detailed memory map for the **Microchip 93LC66** microwire serial EEPROM (512 bytes / 4 Kbit, SOIC-8 package) in M534 (433.92 MHz) and M535 (315 MHz) alarm control units.

The ACU microcontroller (Mitsubishi MELPS 7700 / M37710) utilizes static mask ROM. **100% of vehicle-specific personality, immobilizer pairing, transponder keys, remote fobs, and learning codes reside in this 512-byte EEPROM.**

---

## 1. Quick Reference & Key Offsets

| Data Item | Bank A Offset | Bank B (Mirror) | Size | Format / Example | Purpose |
|:---|:---:|:---:|:---:|:---|:---|
| **Part Number** | `0x009..0x00E` | — | 6 bytes | Packed BCD: `99 66 18 26 00 70` = `996.618.260.07` | ACU hardware/generation identification |
| **OBD Unlock Flag** | `0x080` | — | 2 bytes | `F6 0A` = Unlocked, `00 00` / `55 55` = Factory locked | Enables key learning via diagnostic port |
| **Transponder Slot 1** | `0x0BA` | `0x0CE` | 5 bytes | 4B Megamos ID48 ID + 1B Status (e.g. `94 4C 10 72 BF`) | Engine start transponder authorization |
| **Transponder Slot 2** | `0x0BF` | `0x0D3` | 5 bytes | 4B ID + 1B Status | Key 2 transponder |
| **Transponder Slot 3** | `0x0C4` | `0x0D8` | 5 bytes | 4B ID + 1B Status | Key 3 transponder |
| **Transponder Slot 4** | `0x0C9` | `0x0DD` | 5 bytes | 4B ID + 1B Status | Key 4 transponder |
| **Remote Fob Slot 1** | `0x0E2` | `0x0F7` | 30 bytes | 4B RF ID + 5B Base + 12B Rolling Counter Sync | Keyless entry / RF remote locking |
| **Remote Fob Slot 2** | `0x100` | `0x115` | 30 bytes | 4B RF ID + 5B Base + 12B Rolling Counter Sync | Keyless entry / RF remote locking |
| **Remote Fob Slot 3** | `0x11E` | `0x133` | 30 bytes | 4B RF ID + 5B Base + 12B Rolling Counter Sync | Keyless entry / RF remote locking |
| **Remote Fob Slot 4** | `0x13C` | `0x151` | 30 bytes | 4B RF ID + 5B Base + 12B Rolling Counter Sync | Keyless entry / RF remote locking |
| **PIN (Learning Code)** | `0x1EE` | `0x1F7` | 3 bytes | 6-hex-digit security code (e.g. `DC 4E 40`) | Security PIN for PIWIS/PST2 key learning |
| **ECU Pairing Secret** | `0x1F1` | `0x1FA` | 6 bytes | 12-hex-digit crypto secret (e.g. `3D B8 7A 21 E9 94`) | W-Lead cryptographic link between ACU and DME |

---

## 2. Dual-Bank Architecture (Power-Fail Rollback Protection)

The 93LC66 EEPROM relies on a strict **dual-bank redundancy architecture** (Bank A and Bank B). If a sudden power loss occurs during key programming or battery disconnect, the microcontroller checks Bank A against Bank B:
* **Configuration Blocks:** Block A (`0x020..0x04F`) is mirrored identically in Block B (`0x050..0x07F`).
* **Transponder Slots (40 Bytes Total):**
  * **Bank A:** `0x0BA..0x0CD` (4 slots × 5 bytes = 20 bytes).
  * **Bank B:** `0x0CE..0x0E1` (4 slots × 5 bytes = 20 bytes).
* **Remote Key Fob Slots (120 Bytes Total):**
  * Each remote record spans **30 bytes (`0x1E`)**:
    * **Bank A (21 Bytes):** 4 bytes RF Radio ID + 5 bytes Base Data + 12 bytes Rolling Encryption / Counter Sync.
    * **Bank B (9 Bytes):** Exact mirror of the first 9 bytes of Bank A (`Bank_A[0:9] == Bank_B[0:9]`).
* **PIN & DME Pairing Code (18 Bytes Total):**
  * **Bank A:** `0x1EE..0x1F6` (3 bytes PIN + 6 bytes ECU Pairing Secret).
  * **Bank B:** `0x1F7..0x1FF` (3 bytes PIN + 6 bytes ECU Pairing Secret).

---

## 3. Visual Memory Map (512 Bytes)

```text
 0x000 ┌──────────────────────────────────────────────────────────┐
       │ Header, Serial Number & Manufacturing Date               │
 0x009 ├──────────────────────────────────────────────────────────┤
       │ ACU Part Number (6 bytes BCD, e.g. 99 66 18 26 00 70)    │
 0x00F ├──────────────────────────────────────────────────────────┤
       │ Vehicle Configuration Options (Country, Horn Type, etc.) │
 0x020 ├──────────────────────────────────────────────────────────┤
       │ Configuration Block A (48 bytes)                         │
 0x050 ├──────────────────────────────────────────────────────────┤
       │ Configuration Block B (Mirror of 0x020..0x04F)           │
 0x080 ├──────────────────────────────────────────────────────────┤
       │ ★ OBD Access Control Flags ★ (F6 0A = Unlocked)         │
 0x0A0 ├──────────────────────────────────────────────────────────┤
       │ Diagnostic Authentication & Rolling Seed Region          │
 0x0BA ├──────────────────────────────────────────────────────────┤
       │ ★ TRANSPONDER KEYS BANK A ★ (4 slots × 5 bytes = 20 B)   │
       │ Slot 1: 0x0BA..0x0BE | Slot 2: 0x0BF..0x0C3             │
       │ Slot 3: 0x0C4..0x0C8 | Slot 4: 0x0C9..0x0CD             │
 0x0CE ├──────────────────────────────────────────────────────────┤
       │ ★ TRANSPONDER KEYS BANK B ★ (Exact Mirror of 0x0BA..0x0CD)│
 0x0E2 ├──────────────────────────────────────────────────────────┤
       │ ★ REMOTE FOB SLOT 1 ★ (30 B total: Bank A 21B + Bank B 9B)│
       │ 0x0E2..0x0F6 (Bank A) | 0x0F7..0x0FF (Bank B 9-byte mirror)│
 0x100 ├──────────────────────────────────────────────────────────┤
       │ ★ REMOTE FOB SLOT 2 ★ (30 B total: Bank A 21B + Bank B 9B)│
       │ 0x100..0x114 (Bank A) | 0x115..0x11D (Bank B 9-byte mirror)│
 0x11E ├──────────────────────────────────────────────────────────┤
       │ ★ REMOTE FOB SLOT 3 ★ (30 B total: Bank A 21B + Bank B 9B)│
       │ 0x11E..0x132 (Bank A) | 0x133..0x13B (Bank B 9-byte mirror)│
 0x13C ├──────────────────────────────────────────────────────────┤
       │ ★ REMOTE FOB SLOT 4 ★ (30 B total: Bank A 21B + Bank B 9B)│
       │ 0x13C..0x150 (Bank A) | 0x151..0x159 (Bank B 9-byte mirror)│
 0x15A ├──────────────────────────────────────────────────────────┤
       │ Padding / Unused (`FF FF 00 00 00 00`)                   │
 0x160 ├──────────────────────────────────────────────────────────┤
       │ Reserved Space (0x00 fill)                               │
 0x1B0 ├──────────────────────────────────────────────────────────┤
       │ Counter / Synchronization Region (Pattern: B2 22 D4)    │
 0x1C0 ├──────────────────────────────────────────────────────────┤
       │ Reserved Space (0x00 fill)                               │
 0x1EE ├──────────────────────────────────────────────────────────┤
       │ ★ KEY LEARNING PIN (Bank A, 3 bytes) ★                   │
 0x1F1 ├──────────────────────────────────────────────────────────┤
       │ ★ ECU / DME PAIRING CODE (Bank A, 6 bytes) ★             │
 0x1F7 ├──────────────────────────────────────────────────────────┤
       │ KEY LEARNING PIN (Bank B Mirror, 3 bytes)                │
 0x1FA ├──────────────────────────────────────────────────────────┤
       │ ECU / DME PAIRING CODE (Bank B Mirror, 6 bytes)          │
 0x200 └──────────────────────────────────────────────────────────┘
```

---

## 4. Detailed Field Breakdown

### Part Number BCD Decoding (`0x009..0x00E`)
Stored as 6 consecutive BCD bytes (12 nibbles). Each nibble represents one ASCII digit of the Porsche part number:
```text
Raw Bytes:    99 66 18 26 00 70
Nibble Split: 9 9 6  6 1 8  2 6 0  0 7  0
Part Number:  996 . 618 . 260 . 07
```
Other verified OEM examples:
* `99 66 18 26 00 50` ➔ `996.618.260.05` (Early 986/996 M534/M535)
* `99 66 18 26 20 20` ➔ `996.618.262.02` (Facelift 986/996)
* `99 66 18 26 20 30` ➔ `996.618.262.03` (Facelift late 986/996)

---

### Remote Key Fob Slots (30 Bytes per Slot)
Previous reverse-engineering efforts mistakenly mapped remote slots to 12-byte blocks at `0x100`, `0x10C`, `0x118`, and `0x124`.

**Why this was wrong:**
* `0x100` is actually the start of **Slot 2 (Bank A)**!
* The genuine **Slot 1** begins at **`0x0E2`**!
* Writing a remote to `0x100` overwrites Slot 2, leaves Slot 1 untouched, and corrupts the Bank B mirror.

**Verified 30-Byte Slot Layout:**
Each slot starts at `0x0E2 + (slot_number - 1) * 30`:
```text
Offset Range        Size   Description
──────────────────────────────────────────────────────────────────────
base + 0x00 .. 0x03  4 B   RF Transmitter Radio ID (e.g. 40 08 98 C3)
base + 0x04 .. 0x08  5 B   Transmitter Base Data
base + 0x09 .. 0x14 12 B   Rolling Encryption State & Counter Values
base + 0x15 .. 0x1D  9 B   Bank B Mirror (Exact copy of base + 0x00..0x08)
──────────────────────────────────────────────────────────────────────
```

**Slot Offsets:**
* **Slot 1:** `0x0E2..0x0FF` (Bank A: `0x0E2..0x0F6`, Bank B: `0x0F7..0x0FF`)
* **Slot 2:** `0x100..0x11D` (Bank A: `0x100..0x114`, Bank B: `0x115..0x11D`)
* **Slot 3:** `0x11E..0x13B` (Bank A: `0x11E..0x132`, Bank B: `0x133..0x13B`)
* **Slot 4:** `0x13C..0x159` (Bank A: `0x13C..0x150`, Bank B: `0x151..0x159`)

**Empty / Unprogrammed Slot State:**
An unprogrammed slot displays:
`FF FF FF FF FF FF FF FF B7 FF FF FF FF FF 06 FF FF FF FF FF 06 FF FF FF FF FF FF FF B7`

---

### Megamos ID48 Transponder Slots (`0x0BA..0x0E1`)
Transponder pills used for mechanical ignition starting operate at 125 kHz with a fixed 32-bit (4-byte) hexadecimal identifier.
* **Bank A:** `0x0BA..0x0CD` (4 keys × 5 bytes)
  * Slot 1: `0x0BA..0x0BD` [ID] + `0x0BE` [Status/Separator]
  * Slot 2: `0x0BF..0x0C2` [ID] + `0x0C3` [Status/Separator]
  * Slot 3: `0x0C4..0x0C7` [ID] + `0x0C8` [Status/Separator]
  * Slot 4: `0x0C9..0x0CC` [ID] + `0x0CD` [Status/Separator]
* **Bank B:** `0x0CE..0x0E1` (Exact duplicate mirror of Bank A)

When a key is read by PIWIS or PST2 under *Alarmanlage ➔ Transponder Status*, the 32-bit hex value shown on screen matches the bytes stored at these offsets verbatim.

---

### Key Learning PIN Code (`0x1EE..0x1F0` & `0x1F7..0x1F9`)
A 3-byte (6-character hex) security code used during diagnostic key learning. When teaching keys in PIWIS or PST2, the diagnostic tool prompts for the "Teaching Code / Lerncode". The ACU compares the entered value against `0x1EE`.
* Example: `DC 4E 40` ➔ PIN is `DC4E40`.
* Both `0x1EE` (Bank A) and `0x1F7` (Bank B) must match.

---

### ECU / DME Pairing Code (`0x1F1..0x1F6` & `0x1FA..0x1FF`)
A 6-byte cryptographic secret shared between the Alarm Control Unit and the Engine Control Unit (DME).
* Example: `3D B8 7A 21 E9 94`
* When an engine start is requested, the DME challenges the ACU over the single-wire W-Lead (Pin A23). The ACU computes a response using this 6-byte secret. If the secret in the ACU does not match the secret programmed into the DME EEPROM, the DME denies ignition spark and fuel injection.
