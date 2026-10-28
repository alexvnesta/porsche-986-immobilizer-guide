# Porsche 986/996 ACU Diagnostic & Protocol Reference

The Alarm Control Unit (M534 / M535) communicates with external diagnostic tools (PIWIS, PST2, Durametric, OpenPIWIS) via **ISO 14230 (KWP2000)** over the vehicle K-Line.

---

## 1. Physical Layer & Bus Communication Parameters

| Parameter | Specification | Notes |
|:---|:---:|:---|
| **Diagnostic Pin** | OBD-II Pin 7 | Direct wire to ACU Connector I Pin `A02` (0.35 mm² OG/BK). |
| **Protocol** | ISO 14230-3 on ISO 14230-2 | KWP2000 Fast Initialization. |
| **Baud Rate** | 10,400 bps | Standard Porsche K-Line timing. |
| **Target ECU Address** | `0xC0` | Alarm system physical target identifier. |
| **Tester Address** | `0xF1` | Diagnostic scanner identifier. |
| **Keyword Byte** | `0x80` | Returned during fast init handshake. |
| **Keep-Alive / P3 Timing** | `3E` every 1,500 ms | TesterPresent keep-alive frame. |

### Fast Initialization Sequence
To establish a diagnostic session with the ACU:
```text
Tester sends 25 ms break + 25 ms mark, followed by:
Request:   81 C0 F1 81 53  (StartCommunication to 0xC0)
Response:  83 F1 C0 C1 80 8F 84  (Positive Ack: Keywords 0x80 / 0x8F)
```

---

## 2. Supported KWP2000 Diagnostic Services

| Service | Hex | Sub-Function / Local ID | Description |
|:---|:---:|:---:|:---|
| **StartCommunication** | `0x81` | — | Initializes KWP2000 diagnostic session. |
| **StopCommunication** | `0x82` | — | Closes diagnostic session and returns bus to idle. |
| **TesterPresent** | `0x3E` | — | Periodic keep-alive packet (sent every 1–2 seconds). |
| **ReadEcuIdentification** | `0x1A` | `0x80`, `0x86`, `0x90` | Returns ACU Porsche part number, software release, hardware version. |
| **ReadDiagnosticTroubleCodes** | `0x18` | `0x00 00 00` / `0x02 FF 00` | Reads stored fault memory codes. |
| **ClearDiagnosticInformation** | `0x14` | `FF 00` | Clears stored fault codes. |
| **ReadDataByLocalId** | `0x21` | `0x22` | **Live Digital Inputs:** Reads real-time state of all switches and sensors. |

---

## 3. The `7F 21 33` Negative Response Trap

A frequent source of confusion when building diagnostic software for the 986/996 alarm system is that sending a generic `ReadDataByLocalIdentifier` request (such as `21 01`) results in a **Negative Response**:
```text
Request:   21 01
Response:  7F 21 33  (Negative Response: Conditions Not Correct / Security Access Denied)
```
The ACU firmware does not implement LID `0x01` for general telemetry. Instead, the canonical local identifier for live switch, latch, and sensor monitoring in the factory PIWIS database (`9x6_Alarmanlage.bv.db`) is **Local Identifier `0x22`** (`RQ_9x6_Alarm_TuerenVerriegelnSichern21`).

---

## 4. Live Sensor & Switch Telemetry (Local Identifier `0x22`)

```text
Request:   21 22
Response:  61 22 [Byte 0] [Byte 1] [Byte 2] ...
```

### Bitmask Definitions for LID 0x22:

#### Byte 0: Door Latches & Central Locking
* **Bit 0 (`0x01`):** Driver Door Safe Locked (`0` = Unlocked, `1` = Deadbolted/Safe)
* **Bit 1 (`0x02`):** Passenger Door Safe Locked (`0` = Unlocked, `1` = Deadbolted/Safe)
* **Bit 2 (`0x04`):** Driver Door Locked (`0` = Unlocked, `1` = Locked)
* **Bit 3 (`0x08`):** Passenger Door Locked (`0` = Unlocked, `1` = Locked)
* **Bit 4 (`0x10`):** Driver Door Contact Switch (`0` = Door Closed, `1` = Door Open)
* **Bit 5 (`0x20`):** Passenger Door Contact Switch (`0` = Door Closed, `1` = Door Open)
* **Bit 6 (`0x40`):** Central Locking Dashboard Button (`0` = Released, `1` = Pressed)
* **Bit 7 (`0x80`):** Terminal 86S (`0` = Key Removed, `1` = Key Inserted in Ignition)

#### Byte 1: Ignition, Lids & Storage Microswitches
* **Bit 0 (`0x01`):** Terminal 15 (`0` = Ignition OFF, `1` = Ignition Switched ON)
* **Bit 1 (`0x02`):** Key Lock Cylinder Unlock (`0` = Rest, `1` = Mechanical Key Turned to Unlock)
* **Bit 2 (`0x04`):** Key Lock Cylinder Lock (`0` = Rest, `1` = Mechanical Key Turned to Lock)
* **Bit 3 (`0x08`):** Front Trunk Lid Microswitch (`0` = Hood Closed, `1` = Hood Open)
* **Bit 4 (`0x10`):** Rear Trunk / Engine Lid Microswitch (`0` = Lid Closed, `1` = Lid Open)
* **Bit 5 (`0x20`):** Oddments Box / Glove Compartment (`0` = Closed, `1` = Open)
* **Bit 6 (`0x40`):** Radio Anti-Theft Contact (`0` = Ground Clip Intact, `1` = Stereo Removed/Open)
* **Bit 7 (`0x80`):** Convertible Soft-Top / Hardtop Latches (`0` = Closed/Locked, `1` = Open)

#### Byte 2: Safety & Vehicle State Lines
* **Bit 0 (`0x01`):** Airbag Crash Signal Input (`0` = Normal, `1` = Crash Trigger Active)
* **Bit 1 (`0x02`):** W-Lead Immobilizer Line Status (`0` = Idle/High, `1` = Bus Activity)
* **Bit 2 (`0x04`):** Vehicle Speed Autolock Threshold (`0` = < 3 km/h, `1` = ≥ 3 km/h moving)
* **Bit 3 (`0x08`):** Battery Supply Undervoltage (`0` = Normal voltage ≥ 8.5V, `1` = Low voltage < 8.5V)

---

## 5. Diagnostic Key & Transponder Query Screens

In the factory PIWIS and PST2 menus under **Alarm System ➔ Actual Values / Status**:

1. **Current Transponder ID:**
   * Reads the 32-bit Megamos ID48 transponder identifier currently present inside the inductive antenna ring around the ignition key barrel.
   * Allows validating whether a physical key is transmitting its ID before attempting to start the car.
2. **Enrolled Transponder Positions (1 to 4):**
   * Displays the 4 stored IDs in EEPROM Bank A (`0x0BA..0x0CD`).
   * Verifies which physical key matches which registered slot.
3. **Current Radio Key ID:**
   * Displays the 32-bit RF identifier transmitted by the most recent remote fob button press.
   * Validates whether the ACU receiver daughterboard is receiving RF signals from the fob.
4. **Enrolled Radio Key Fobs (1 to 4):**
   * Displays the 4 registered remote fobs from EEPROM (`0x0E2`, `0x100`, `0x11E`, `0x13C`).

---

## 6. Parameter Coding Options (KWP2000 Write)

PIWIS supports field coding of configuration bytes in the ACU EEPROM via diagnostic routines:
* **Country Coding:** Rest of World (RoW), USA, Canada, Great Britain, Belgium.
* **Acoustic Arming Chirp:** Enables or disables the short horn beep when locking/unlocking.
* **Interior Passenger Compartment Radar Sensor:** Enables or disables the radar motion sensor (useful when troubleshooting false alarm triggers with the convertible top down).
* **Speed-Dependent Central Locking:** Automatically deadbolts door latches when vehicle speed exceeds 3 km/h.
