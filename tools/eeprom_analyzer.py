#!/usr/bin/env python3
"""
Porsche 986/996 ACU EEPROM Analyzer
Extracts and displays all known codes and data from a 93LC66 EEPROM dump.

Usage:
    python3 eeprom_analyzer.py <eeprom.bin> [--compare <other.bin>]

Repository: https://github.com/YOUR_USERNAME/porsche-986-immobilizer-guide
"""

import sys
import argparse

def format_hex(data, start_offset=0, bytes_per_line=16):
    """Format bytes as a hex dump with ASCII representation."""
    lines = []
    for i in range(0, len(data), bytes_per_line):
        hex_part = ' '.join(f'{b:02X}' for b in data[i:i+bytes_per_line])
        ascii_part = ''.join(chr(b) if 32 <= b < 127 else '.' for b in data[i:i+bytes_per_line])
        lines.append(f'{start_offset + i:04X}: {hex_part:<48} {ascii_part}')
    return '\n'.join(lines)


def analyze_part_number(data):
    """Decode the ACU part number from bytes at 0x009."""
    if len(data) < 0x00F:
        return "Unknown (data too short)"
    
    part_bytes = data[0x009:0x00F]
    # Format: 99 66 18 26 00 70 -> 996.618.260.07
    try:
        pn = f"{part_bytes[0]:02X}{part_bytes[1]:02X}.{part_bytes[2]:02X}{part_bytes[3]:02X}.{part_bytes[4]:02X}{part_bytes[5]:02X}"
        # Clean up formatting
        decoded = f"{int(part_bytes[0]):d}{int(part_bytes[1]):02d}.{int(part_bytes[2]):d}{int(part_bytes[3]):02d}.{int(part_bytes[4]):d}{int(part_bytes[5]):02d}"
        return f"{' '.join(f'{b:02X}' for b in part_bytes)} -> {decoded}"
    except:
        return f"{' '.join(f'{b:02X}' for b in part_bytes)} (decode failed)"


def analyze_pin(data):
    """Extract PIN/Key Learning Code from 0x1EE and 0x1F7."""
    if len(data) < 0x1FA:
        return None, None, False

    pin1 = data[0x1EE:0x1F1]
    pin2 = data[0x1F7:0x1FA]
    match = (pin1 == pin2)

    return pin1, pin2, match


def analyze_ecu_pairing(data):
    """Extract ECU pairing code from 0x1F1 and 0x1FA."""
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


def analyze_remote_slot(data, slot_num):
    """Analyze a remote control slot."""
    offsets = {1: 0x100, 2: 0x10C, 3: 0x118, 4: 0x124}
    
    if slot_num not in offsets:
        return None, "Invalid slot"
    
    offset = offsets[slot_num]
    if len(data) < offset + 12:
        return None, "Data too short"
    
    slot_data = data[offset:offset+12]
    
    # Check if slot is empty/unprogrammed
    unique_vals = set(slot_data)
    if unique_vals <= {0xFF, 0xB7, 0x06}:
        return slot_data, "EMPTY (unprogrammed pattern)"
    elif all(b == 0x00 for b in slot_data):
        return slot_data, "EMPTY (all zeros)"
    elif all(b == 0xFF for b in slot_data):
        return slot_data, "EMPTY (all 0xFF)"
    else:
        return slot_data, "PROGRAMMED"


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
    print("\n[OBD PROGRAMMING STATUS]")
    print("-" * 40)
    obd_status = analyze_obd_status(data)
    print(f"  {obd_status}")

    # PIN Code
    print("\n[PIN / KEY LEARNING CODE]")
    print("-" * 40)
    pin1, pin2, match = analyze_pin(data)
    if pin1:
        print(f"  Location 0x1EE: {' '.join(f'{b:02X}' for b in pin1)}")
        print(f"  Location 0x1F7: {' '.join(f'{b:02X}' for b in pin2)}")
        if match:
            print(f"\n  ✓ PIN codes match")
            print(f"\n  >>> YOUR PIN: {' '.join(f'{b:02X}' for b in pin1)} <<<")
        else:
            print(f"\n  ⚠ WARNING: PIN codes do NOT match!")

    # ECU Pairing Code
    print("\n[ECU PAIRING CODE (Alarm Learning Code)]")
    print("-" * 40)
    pairing1, pairing2, pairing_match = analyze_ecu_pairing(data)
    if pairing1:
        print(f"  Location 0x1F1: {' '.join(f'{b:02X}' for b in pairing1)}")
        print(f"  Location 0x1FA: {' '.join(f'{b:02X}' for b in pairing2)}")
        if pairing_match:
            print(f"\n  ✓ Pairing codes match")
            print(f"\n  >>> ECU PAIRING: {' '.join(f'{b:02X}' for b in pairing1)} <<<")
        else:
            print(f"\n  ⚠ WARNING: Pairing codes do NOT match!")
    
    # Remote Slots
    print("\n[REMOTE CONTROL SLOTS] (0x100-0x13F)")
    print("-" * 40)
    for slot in range(1, 5):
        slot_data, status = analyze_remote_slot(data, slot)
        if slot_data:
            hex_str = ' '.join(f'{b:02X}' for b in slot_data)
            print(f"  Slot {slot}: {status}")
            print(f"         {hex_str}")
    
    # Sync Region
    print("\n[COUNTER/SYNC REGION] (0x1B0-0x1BF)")
    print("-" * 40)
    sync_data = analyze_sync_region(data)
    if sync_data:
        print(f"  {' '.join(f'{b:02X}' for b in sync_data)}")
        # Check for known sync pattern
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
    
    # Key data region
    print("\n[KEY DATA REGION] (0x090-0x0AF)")
    print("-" * 40)
    if len(data) >= 0x0B0:
        print(format_hex(data[0x090:0x0B0], 0x090))
    
    # Transponder region
    print("\n[TRANSPONDER REGION] (0x0B0-0x0DF)")
    print("-" * 40)
    if len(data) >= 0x0E0:
        print(format_hex(data[0x0B0:0x0E0], 0x0B0))
    
    # PIN region detail
    print("\n[PIN REGION DETAIL] (0x1E0-0x1FF)")
    print("-" * 40)
    if len(data) >= 0x200:
        print(format_hex(data[0x1E0:0x200], 0x1E0))
    
    # Full dump option
    print("\n" + "=" * 70)
    print("FULL HEX DUMP")
    print("=" * 70)
    print(format_hex(data))
    
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
        print(f"⚠ Files have different sizes!")
    
    print(f"\nTotal differences: {len(differences)} bytes")
    
    if differences:
        print("\nOffset   File1  File2  Region")
        print("-" * 50)
        
        for offset, b1, b2 in differences[:100]:
            # Determine region
            if 0x009 <= offset <= 0x00E:
                region = "Part Number"
            elif 0x080 <= offset <= 0x08F:
                region = "OBD Flags ★"
            elif 0x0A0 <= offset <= 0x0AF:
                region = "Auth Bypass ★"
            elif 0x0B0 <= offset <= 0x0B6:
                region = "Unlock Data ★"
            elif 0x100 <= offset <= 0x15F:
                region = "Remote Slots"
            elif 0x1EE <= offset <= 0x1F0 or 0x1F7 <= offset <= 0x1F9:
                region = "PIN Code"
            elif 0x1F1 <= offset <= 0x1F6 or 0x1FA <= offset <= 0x1FF:
                region = "ECU Pairing"
            elif 0x1B0 <= offset <= 0x1BF:
                region = "Sync Region"
            elif 0x090 <= offset <= 0x09F:
                region = "Key Data"
            elif 0x0B7 <= offset <= 0x0FF:
                region = "Transponder"
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
