#!/usr/bin/env python3
"""
Porsche 986/996 ACU EEPROM Analyzer
Extracts and displays all known codes, transponder keys, remote fobs, and dual-bank
redundancy status from a 93LC66 EEPROM dump.

Usage:
    python3 eeprom_analyzer.py <eeprom.bin> [--compare <other.bin>]

Repository: https://github.com/alexvnesta/porsche-986-immobilizer-guide
"""

import sys
import argparse

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass


def format_hex(data, start_offset=0, bytes_per_line=16):
    """Format bytes as a hex dump with ASCII representation."""
    lines = []
    for i in range(0, len(data), bytes_per_line):
        hex_part = ' '.join(f'{b:02X}' for b in data[i:i+bytes_per_line])
        ascii_part = ''.join(chr(b) if 32 <= b < 127 else '.' for b in data[i:i+bytes_per_line])
        lines.append(f'{start_offset + i:04X}: {hex_part:<48} {ascii_part}')
    return '\n'.join(lines)


def analyze_part_number(data):
    """Decode the ACU part number from packed BCD bytes at 0x009..0x00E."""
    if len(data) < 0x00F:
        return "Unknown (data too short)"

    part_bytes = data[0x009:0x00F]
    pn_hex = part_bytes.hex()
    # 12 nibbles packed BCD: e.g. 996618260070 -> 996.618.260.07
    try:
        formatted = f"{pn_hex[0:3]}.{pn_hex[3:6]}.{pn_hex[6:9]}.{pn_hex[9:11]}"
        return f"{' '.join(f'{b:02X}' for b in part_bytes)} -> {formatted}"
    except Exception:
        return f"{' '.join(f'{b:02X}' for b in part_bytes)} (decode failed)"


def analyze_pin(data):
    """Extract PIN/Key Learning Code from Bank A (0x1EE) and Bank B (0x1F7)."""
    if len(data) < 0x1FA:
        return None, None, False

    pin1 = data[0x1EE:0x1F1]
    pin2 = data[0x1F7:0x1FA]
    match = (pin1 == pin2)

    return pin1, pin2, match


def analyze_ecu_pairing(data):
    """Extract 6-byte ECU pairing code from Bank A (0x1F1) and Bank B (0x1FA)."""
    if len(data) < 0x200:
        return None, None, False

    pairing1 = data[0x1F1:0x1F7]
    pairing2 = data[0x1FA:0x200]
    match = (pairing1 == pairing2)

    return pairing1, pairing2, match


def analyze_obd_status(data):
    """Check if OBD programming access is enabled."""
    if len(data) < 0x086:
        return "Unknown (data too short)"

    # Check for the F6 0A unlock pattern at 0x080 and 0x083
    flag1 = data[0x080:0x082]
    flag2 = data[0x083:0x085]
    unlocked_pattern = bytes([0xF6, 0x0A])

    if flag1 == unlocked_pattern and flag2 == unlocked_pattern:
        return "UNLOCKED (OBD programming enabled)"
    elif flag1 == bytes([0x00, 0x00]) or flag2 == bytes([0x55, 0x55]):
        return "LOCKED (OBD programming disabled)"
    else:
        return f"UNKNOWN (flags: {flag1.hex()} / {flag2.hex()})"


def analyze_transponders(data):
    """Analyze the 4 Megamos ID48 transponder slots (Bank A vs Bank B mirror)."""
    if len(data) < 0x0E2:
        return []

    slots = []
    for slot in range(4):
        off_a = 0x0BA + (slot * 5)
        off_b = 0x0CE + (slot * 5)

        id_a = data[off_a:off_a + 4]
        sep_a = data[off_a + 4]
        id_b = data[off_b:off_b + 4]
        sep_b = data[off_b + 4]

        is_empty = (id_a == bytes([0xFF, 0xFF, 0xFF, 0xFF]) or id_a == bytes([0x00, 0x00, 0x00, 0x00]))
        matches = (id_a == id_b)

        slots.append({
            'slot': slot + 1,
            'offset_a': off_a,
            'id_a': id_a.hex().upper(),
            'id_b': id_b.hex().upper(),
            'sep_a': f"{sep_a:02X}",
            'empty': is_empty,
            'matches': matches
        })
    return slots


def analyze_remote_slot(data, slot_num):
    """Analyze a remote control slot (30 bytes per slot: 21B Bank A + 9B Bank B mirror)."""
    if slot_num not in [1, 2, 3, 4]:
        return None, "Invalid slot", False

    # Base offsets: Slot 1: 0x0E2, Slot 2: 0x100, Slot 3: 0x11E, Slot 4: 0x13C
    base_a = 0x0E2 + (slot_num - 1) * 30
    base_b = base_a + 21

    if len(data) < base_a + 30:
        return None, "Data too short", False

    bank_a_record = data[base_a:base_a + 21]
    bank_b_record = data[base_b:base_b + 9]

    rf_id = bank_a_record[0:4]
    is_empty = (rf_id == bytes([0xFF, 0xFF, 0xFF, 0xFF]) or rf_id == bytes([0x00, 0x00, 0x00, 0x00]))
    mirror_match = (bank_a_record[0:9] == bank_b_record)

    if is_empty:
        status = "EMPTY"
    elif mirror_match:
        status = "PROGRAMMED (Bank Mirror Valid)"
    else:
        status = "DESYNCHRONIZED (Bank Mirror Mismatch)"

    slot_info = {
        'rf_id': rf_id.hex().upper(),
        'base_a': base_a,
        'base_b': base_b,
        'bank_a_hex': bank_a_record.hex().upper(),
        'bank_b_hex': bank_b_record.hex().upper(),
    }
    return slot_info, status, mirror_match


def analyze_sync_region(data):
    """Analyze the counter/sync region at 0x1B0."""
    if len(data) < 0x1C0:
        return None
    return data[0x1B0:0x1C0]


def print_analysis(filepath):
    """Main analysis function."""
    with open(filepath, 'rb') as f:
        data = f.read()

    print("=" * 70)
    print("PORSCHE 986/996 ACU EEPROM ANALYSIS")
    print("=" * 70)
    print(f"File: {filepath}")
    print(f"Size: {len(data)} bytes")

    if len(data) != 512:
        print(f"⚠ WARNING: Expected 512 bytes for 93LC66, got {len(data)}")

    print("=" * 70)

    # Part Number
    print("\n[PART NUMBER] (0x009-0x00E)")
    print("-" * 40)
    print(f"  {analyze_part_number(data)}")

    # OBD Status
    print("\n[OBD PROGRAMMING STATUS] (0x080)")
    print("-" * 40)
    obd_status = analyze_obd_status(data)
    print(f"  {obd_status}")

    # PIN Code
    print("\n[PIN / KEY LEARNING CODE]")
    print("-" * 40)
    pin1, pin2, match = analyze_pin(data)
    if pin1:
        print(f"  Bank A (0x1EE): {' '.join(f'{b:02X}' for b in pin1)}")
        print(f"  Bank B (0x1F7): {' '.join(f'{b:02X}' for b in pin2)}")
        if match:
            print(f"  ✓ PIN codes match: {' '.join(f'{b:02X}' for b in pin1)}")
        else:
            print("  ⚠ WARNING: PIN codes do NOT match!")

    # ECU Pairing Code
    print("\n[ECU PAIRING CODE (W-Lead Secret)]")
    print("-" * 40)
    pairing1, pairing2, pairing_match = analyze_ecu_pairing(data)
    if pairing1:
        print(f"  Bank A (0x1F1): {' '.join(f'{b:02X}' for b in pairing1)}")
        print(f"  Bank B (0x1FA): {' '.join(f'{b:02X}' for b in pairing2)}")
        if pairing_match:
            print(f"  ✓ Pairing codes match: {' '.join(f'{b:02X}' for b in pairing1)}")
        else:
            print("  ⚠ WARNING: Pairing codes do NOT match!")

    # Transponders
    print("\n[TRANSPONDER KEYS (Megamos ID48)] (0x0BA-0x0E1)")
    print("-" * 40)
    transponders = analyze_transponders(data)
    for t in transponders:
        if t['empty']:
            print(f"  Slot {t['slot']} (0x{t['offset_a']:03X}): [Empty slot] (Separator: 0x{t['sep_a']})")
        else:
            status = "✓ Bank A == Bank B" if t['matches'] else "⚠ Bank mismatch"
            print(f"  Slot {t['slot']} (0x{t['offset_a']:03X}): ID = {t['id_a']} (Sep: 0x{t['sep_a']}) [{status}]")

    # Remote Slots
    print("\n[REMOTE CONTROL SLOTS] (0x0E2-0x159, 30 bytes per slot)")
    print("-" * 40)
    for slot in range(1, 5):
        slot_info, status, mirror_match = analyze_remote_slot(data, slot)
        if slot_info:
            print(f"  Slot {slot} (0x{slot_info['base_a']:03X}): {status}")
            if "PROGRAMMED" in status:
                print(f"         Radio ID: {slot_info['rf_id']}")
                print(f"         Bank A (21B): {slot_info['bank_a_hex']}")
                print(f"         Bank B (9B):  {slot_info['bank_b_hex']}")

    # Sync Region
    print("\n[COUNTER/SYNC REGION] (0x1B0-0x1BF)")
    print("-" * 40)
    sync_data = analyze_sync_region(data)
    if sync_data:
        print(f"  {' '.join(f'{b:02X}' for b in sync_data)}")
        if bytes([0xB2, 0x22, 0xD4]) in sync_data:
            print("  ✓ Found sync pattern: B2 22 D4")

    # Configuration blocks
    print("\n[CONFIGURATION COMPARISON]")
    print("-" * 40)
    if len(data) >= 0x080:
        block1 = data[0x020:0x050]
        block2 = data[0x050:0x080]
        if block1 == block2:
            print("  ✓ Config blocks at 0x020 and 0x050 match (normal)")
        else:
            print("  ⚠ Config blocks at 0x020 and 0x050 differ (unusual)")

    return data


def compare_dumps(file1, file2):
    """Compare two EEPROM dumps and highlight differences."""
    with open(file1, 'rb') as f:
        data1 = f.read()
    with open(file2, 'rb') as f:
        data2 = f.read()

    print("\n" + "=" * 70)
    print("EEPROM COMPARISON")
    print("=" * 70)
    print(f"File 1: {file1} ({len(data1)} bytes)")
    print(f"File 2: {file2} ({len(data2)} bytes)")
    print("-" * 70)

    min_len = min(len(data1), len(data2))
    differences = []

    for i in range(min_len):
        if data1[i] != data2[i]:
            differences.append((i, data1[i], data2[i]))

    if len(data1) != len(data2):
        print("⚠ Files have different sizes!")

    print(f"\nTotal differences: {len(differences)} bytes")

    if differences:
        print("\nOffset   File1  File2  Region")
        print("-" * 50)

        for offset, b1, b2 in differences[:100]:
            if 0x009 <= offset <= 0x00E:
                region = "Part Number"
            elif 0x080 <= offset <= 0x08F:
                region = "OBD Flags ★"
            elif 0x0A0 <= offset <= 0x0AF:
                region = "Auth Bypass ★"
            elif 0x0B0 <= offset <= 0x0B6:
                region = "Unlock Data ★"
            elif 0x0BA <= offset <= 0x0CD:
                region = "Transponder Bank A"
            elif 0x0CE <= offset <= 0x0E1:
                region = "Transponder Bank B"
            elif 0x0E2 <= offset <= 0x159:
                region = "Remote Slots"
            elif 0x1EE <= offset <= 0x1F0 or 0x1F7 <= offset <= 0x1F9:
                region = "PIN Code"
            elif 0x1F1 <= offset <= 0x1F6 or 0x1FA <= offset <= 0x1FF:
                region = "ECU Pairing"
            elif 0x1B0 <= offset <= 0x1BF:
                region = "Sync Region"
            else:
                region = ""

            print(f"0x{offset:04X}   0x{b1:02X}   0x{b2:02X}   {region}")

        if len(differences) > 100:
            print(f"... and {len(differences) - 100} more differences")
    else:
        print("\n✓ Files are identical!")


def main():
    parser = argparse.ArgumentParser(
        description='Porsche 986/996 ACU EEPROM Analyzer',
        epilog='Example: python3 eeprom_analyzer.py my_dump.bin --compare donor.bin'
    )
    parser.add_argument('eeprom', help='EEPROM dump file (512 bytes)')
    parser.add_argument('--compare', '-c', help='Compare with another EEPROM dump')

    args = parser.parse_args()

    try:
        print_analysis(args.eeprom)
        if args.compare:
            compare_dumps(args.eeprom, args.compare)
    except FileNotFoundError as e:
        print(f"Error: File not found - {e.filename}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
