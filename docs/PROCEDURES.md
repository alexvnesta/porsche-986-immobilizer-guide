# Porsche 986/996 Key Programming Procedures

Step-by-step procedures for programming transponders and remotes.

## Table of Contents

1. [Reading the EEPROM](#1-reading-the-eeprom)
2. [Extracting the PIN Code](#2-extracting-the-pin-code)
3. [Programming a Remote via EEPROM](#3-programming-a-remote-via-eeprom)
4. [Programming a Transponder via PIWIS](#4-programming-a-transponder-via-piwis)
5. [Programming a Remote via PIWIS](#5-programming-a-remote-via-piwis)
6. [Enabling OBD Programming Access](#6-enabling-obd-programming-access)
7. [Cloning a Water-Damaged ACU](#7-cloning-a-water-damaged-acu)

---

## 1. Reading the EEPROM

### Equipment Needed

- CH341A USB programmer
- SOIC-8 test clip
- AsProgrammer software (or equivalent)
- Computer with USB port

### Procedure

1. **Remove the ACU from the car**
   - Located under driver's seat
   - Quarter-turn lock mechanism
   - Slide forward to release rear clip
   - Disconnect harness

2. **Open the ACU case**
   - Remove screws from case
   - Carefully separate housing

3. **Locate the 93LC66 EEPROM**
   - Small 8-pin SOIC chip near main processor
   - Usually marked "93LC66" or "93C66"

4. **Connect the SOIC-8 clip**
   - Align pin 1 (dot on chip) with pin 1 on clip
   - Ensure good contact on all pins
   - Connect clip cable to CH341A

5. **Read the EEPROM**
   ```
   Software: AsProgrammer
   Chip: 93C66 (select from list)
   Mode: 8-bit (important!)
   Size: 512 bytes
   ```
   
6. **Read twice and compare**
   - Click "Read" 
   - Save as `read1.bin`
   - Click "Read" again
   - Save as `read2.bin`
   - Compare files - they must be identical

7. **Save your backup**
   - Keep the original file safe!
   - Name it something like `MY_CAR_ACU_ORIGINAL.bin`

### Troubleshooting

**Can't detect chip:**
- Check clip alignment
- Clean chip pins with isopropyl alcohol
- Try grounding the processor's oscillator pin

**Inconsistent reads:**
- Reduce read speed if possible
- Check for bent clip pins
- Ensure power supply is stable

---

## 2. Extracting the PIN Code

### From Hex Editor

1. Open your EEPROM dump in a hex editor (HxD, etc.)

2. Navigate to offset `0x1EE`

3. Read 3 bytes - this is your PIN
   ```
   Example at 0x1EE: DC 4E 40
   Your PIN is: DC 4E 40
   ```

4. Verify at offset `0x1F7` - should be identical
   ```
   Example at 0x1F7: DC 4E 40 ✓
   ```

### Using the Python Script

```bash
python3 eeprom_analyzer.py your_dump.bin
```

Output will include:
```
>>> YOUR PIN CODE: DC 4E 40 <<<
```

### PIN Format for PIWIS

When PIWIS asks for the "Key Learning Code" or "Teach Enable Code":
- Enter all 3 bytes as 6 hex characters
- Example: `DC4E40` or `DC 4E 40` depending on interface

---

## 3. Programming a Remote via EEPROM

This method writes the remote code directly to the EEPROM without needing PIWIS.

### Requirements

- EEPROM dump from your ACU
- New remote PCB with barcode tag
- CH341A programmer

### Procedure

1. **Get the 24-character code from your remote's barcode**
   ```
   Example barcode: 40 05 90 50 23 6E 31 7F 29 18 D8 21
   As string: 40059050236E317F2918D821
   ```

2. **Run the programming script**
   ```bash
   python3 program_remote.py original.bin modified.bin 1 40059050236E317F2918D821
   ```
   
   Parameters:
   - `original.bin` - Your EEPROM backup
   - `modified.bin` - Output file
   - `1` - Slot number (1-4)
   - `40059050...` - 24-character barcode code

3. **Verify the modification**
   ```bash
   python3 eeprom_analyzer.py modified.bin
   ```
   
   Check that Remote Slot 1 now shows "PROGRAMMED"

4. **Flash the modified EEPROM**
   - Connect SOIC clip to ACU
   - Open modified.bin in AsProgrammer
   - Click "Write"
   - Click "Verify" to confirm

5. **Reinstall ACU and test**
   - Install ACU in car
   - Test remote lock/unlock function
   - If not working immediately, press button 2-3 times to sync

### Multiple Remotes

To program additional remotes:
```bash
# Remote 2
python3 program_remote.py modified.bin modified2.bin 2 SECOND24CHARCODE

# Remote 3
python3 program_remote.py modified2.bin modified3.bin 3 THIRD24CHARCODE
```

---

## 4. Programming a Transponder via PIWIS

Programs a new ID48 chip to allow the car to START.

### Requirements

- PIWIS/PST2 diagnostic tool
- Your PIN code (from EEPROM)
- Blank ID48 transponder chip
- Key blade (cut to match your locks)

### Procedure

1. **Connect PIWIS to car**
   - OBD-II port (under dash, driver's side)
   - Turn ignition to ON (not start)

2. **Navigate to key programming**
   ```
   Diagnostics
   └── Boxster (986) / 911 (996)
       └── Alarm
           └── Maintenance / Repairs
               └── Teach Keys
   ```

3. **Enter your PIN code**
   - PIWIS will prompt for "Key Learning Code"
   - Enter your 3-byte PIN: `DC 4E 40`

4. **Select key position**
   - PIWIS shows slots 1-4
   - Choose an empty slot

5. **Insert new key and learn**
   - Insert key with new transponder into ignition
   - Turn to ON position
   - Click "Learn" in PIWIS

6. **Verify programming**
   - Remove key
   - Re-insert and try to start car
   - Engine should crank and start

### Notes

- You can have up to 4 transponders programmed
- The transponder only allows STARTING - not lock/unlock
- A "valet key" uses transponder only (no remote)

---

## 5. Programming a Remote via PIWIS

Programs the RF remote for lock/unlock functions.

### Requirements

- PIWIS/PST2 diagnostic tool
- Your PIN code (from EEPROM)
- New remote with barcode tag (24-character code)

### Procedure

1. **Connect PIWIS to car**

2. **Navigate to remote programming**
   ```
   Diagnostics
   └── Boxster (986) / 911 (996)
       └── Alarm
           └── Maintenance / Repairs
               └── Teach Remote Control
   ```

3. **Enter your PIN code**
   - Enter 3-byte PIN when prompted

4. **Enter remote barcode code**
   - PIWIS will prompt for the remote code
   - Enter all 24 characters from barcode
   - Example: `40059050236E317F2918D821`

5. **Select slot and learn**
   - Choose slot 1-4
   - Click "Learn"

6. **Test remote**
   - Exit PIWIS
   - Test lock/unlock from outside car

---

## 6. Enabling OBD Programming Access

Some ACUs have OBD programming disabled. If PIWIS shows "No access authorization", follow this procedure.

### Using ABRITES

1. Read EEPROM from ACU
2. In ABRITES, go to:
   ```
   Dump Tool
   └── Porsche (9x6)
       └── Enable Alarm module access by OBD2
   ```
3. Load your EEPROM dump
4. Click "Save" - ABRITES modifies the necessary bytes
5. Write modified EEPROM back to ACU

### Manual Method (Advanced)

The OBD unlock requires modifying **THREE regions** (39 bytes total):

#### Region 1: OBD Flags (0x080-0x08F)
```
Locked:   00 00 00 55 55 00 50 75 30 50 03 30 00 05 00 00
Unlocked: F6 0A 00 F6 0A 00 75 00 00 30 30 01 03 02 00 00
```

#### Region 2: Authentication Bypass (0x0A0-0x0AF)
```
Locked:   00 00 7A 7A 75 7A 75 73 75 75 7A 7A 00 00 00 00
Unlocked: 00 00 8B 3B 3B 3B 3B EB 3B 3B E6 3B 64 A0 A0 3D
```

#### Region 3: Additional Unlock (0x0B0-0x0B6)
```
Locked:   00 00 00 00 00 00 4C
Unlocked: 3D 85 E5 E5 E5 63 0C
```

**These values are UNIVERSAL** - confirmed identical across multiple unlocked dumps from different sources (ABRITES, Digital Kaos forum, YouTube).

#### Complete Unlock Patch
Write these bytes to your EEPROM:
```
0x080: F6 0A 00 F6 0A 00 75 00 00 30 30 01 03 02 00 00
0x0A0: 00 00 8B 3B 3B 3B 3B EB 3B 3B E6 3B 64 A0 A0 3D
0x0B0: 3D 85 E5 E5 E5 63 0C
```

**WARNING:** Always backup your original EEPROM first!

---

## 7. Cloning a Water-Damaged ACU

If your ACU has water damage but the EEPROM is intact, you can clone to a replacement ACU.

### Procedure

1. **Read EEPROM from damaged ACU**
   - Even if ACU doesn't work, EEPROM may be readable
   - Save as `damaged_acu.bin`

2. **Obtain a donor ACU**
   - Must be same version (M534 vs M535)
   - Must be same part number series (260 vs 262)
   - Frequency must match (315 MHz vs 433 MHz)

3. **Read donor EEPROM**
   - Save as `donor_acu.bin`
   - This is your backup of donor

4. **Write your EEPROM to donor**
   - Write `damaged_acu.bin` to donor's EEPROM
   - Verify write completed successfully

5. **Install donor ACU in car**
   - Should work with your existing keys
   - All programming transfers with EEPROM

### Important Notes

- Donor ACU's original VIN/data will be overwritten
- Keys from donor car will NOT work after clone
- This effectively makes donor ACU "yours"

---

## Quick Reference Card

### PIN Location
```
Offset 0x1EE (3 bytes) - Primary
Offset 0x1F7 (3 bytes) - Backup (must match)
```

### Remote Slot Locations
```
Slot 1: 0x100 (12 bytes)
Slot 2: 0x10C (12 bytes)
Slot 3: 0x118 (12 bytes)
Slot 4: 0x124 (12 bytes)
```

### Part Number Location
```
Offset 0x009 (6 bytes)
Example: 99 66 18 26 00 70 = 996.618.260.07
```

### PIWIS Navigation
```
Diagnostics → Model → Alarm → Maintenance/Repairs → 
  ├── Teach Keys (transponder)
  └── Teach Remote Control (remote)
```
