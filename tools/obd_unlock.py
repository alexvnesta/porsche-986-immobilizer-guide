#!/usr/bin/env python3
"""
Porsche 986/996 ACU OBD Unlock Tool
Enables or disables OBD-II programming access in EEPROM dumps.

Usage:
    python3 obd_unlock.py <input.bin> <output.bin> [--lock]
    python3 obd_unlock.py <input.bin> --check

Examples:
    # Check current OBD status
    python3 obd_unlock.py my_eeprom.bin --check

    # Unlock OBD access (enable programming via diagnostic port)
    python3 obd_unlock.py locked.bin unlocked.bin

    # Lock OBD access (disable programming via diagnostic port)
    python3 obd_unlock.py unlocked.bin locked.bin --lock

What this does:
    The ACU has an anti-theft feature that prevents key programming via
    OBD-II even with the correct PIN. This tool modifies three EEPROM
    regions to enable/disable that access:

    - 0x080-0x08F: OBD access flags (F6 0A = enabled)
    - 0x0A0-0x0AF: Authentication bypass values
    - 0x0B0-0x0B6: Additional unlock data

    The unlock values are UNIVERSAL - they work across all M534/M535 modules.

Repository: https://github.com/alexvnesta/porsche-986-immobilizer-guide
"""

import sys
import os
import argparse

# Universal OBD unlock bytes (confirmed across multiple ABRITES unlocks)
UNLOCK_REGION_1 = bytes.fromhex('F6 0A 00 F6 0A 00 75 00 00 30 30 01 03 02 00 00'.replace(' ', ''))
UNLOCK_REGION_2 = bytes.fromhex('00 00 8B 3B 3B 3B 3B EB 3B 3B E6 3B 64 A0 A0 3D'.replace(' ', ''))
UNLOCK_REGION_3 = bytes.fromhex('3D 85 E5 E5 E5 63 0C'.replace(' ', ''))

# Typical locked state bytes (may vary slightly between modules)
LOCK_REGION_1 = bytes.fromhex('00 00 00 55 55 00 50 75 30 50 03 30 00 05 00 00'.replace(' ', ''))
LOCK_REGION_2 = bytes.fromhex('00 00 7A 7A 75 7A 75 73 75 75 7A 7A 00 00 00 00'.replace(' ', ''))
LOCK_REGION_3 = bytes.fromhex('00 00 00 00 00 00 4C'.replace(' ', ''))

# Offsets
OFFSET_REGION_1 = 0x080
OFFSET_REGION_2 = 0x0A0
OFFSET_REGION_3 = 0x0B0


def format_hex(data):
    """Format bytes as hex string."""
    return ' '.join(f'{b:02X}' for b in data)


def check_obd_status(data):
    """
    Check OBD unlock status.
    Returns: 'unlocked', 'locked', or 'unknown'
    """
    if len(data) < 0x0B7:
        return 'unknown', "Data too short"

    region1 = data[OFFSET_REGION_1:OFFSET_REGION_1 + 16]

    # Check for unlock signature (F6 0A at 0x080 and 0x083)
    if region1[0:2] == bytes([0xF6, 0x0A]) and region1[3:5] == bytes([0xF6, 0x0A]):
        return 'unlocked', "F6 0A flags detected at 0x080 and 0x083"

    # Check for common locked patterns
    if region1[0:2] == bytes([0x00, 0x00]):
        return 'locked', "00 00 flags at 0x080 (typical locked state)"

    return 'unknown', f"Unrecognized pattern at 0x080: {format_hex(region1[0:6])}"


def verify_eeprom(data):
    """Verify the EEPROM data looks valid."""
    issues = []

    if len(data) != 512:
        issues.append(f"Size is {len(data)} bytes, expected 512")

    if all(b == 0x00 for b in data):
        issues.append("Data is all zeros - likely a bad read")
    if all(b == 0xFF for b in data):
        issues.append("Data is all 0xFF - likely erased or bad read")

    # Check PIN locations match
    if len(data) >= 0x1FA:
        pin1 = data[0x1EE:0x1F1]
        pin2 = data[0x1F7:0x1FA]
        if pin1 != pin2:
            issues.append("PIN codes at 0x1EE and 0x1F7 don't match - possible corruption")

    return issues


def unlock_obd(data):
    """Apply OBD unlock patch to EEPROM data."""
    data = bytearray(data)

    # Write all three unlock regions
    data[OFFSET_REGION_1:OFFSET_REGION_1 + len(UNLOCK_REGION_1)] = UNLOCK_REGION_1
    data[OFFSET_REGION_2:OFFSET_REGION_2 + len(UNLOCK_REGION_2)] = UNLOCK_REGION_2
    data[OFFSET_REGION_3:OFFSET_REGION_3 + len(UNLOCK_REGION_3)] = UNLOCK_REGION_3

    return bytes(data)


def lock_obd(data):
    """Apply OBD lock patch to EEPROM data."""
    data = bytearray(data)

    # Write all three lock regions
    data[OFFSET_REGION_1:OFFSET_REGION_1 + len(LOCK_REGION_1)] = LOCK_REGION_1
    data[OFFSET_REGION_2:OFFSET_REGION_2 + len(LOCK_REGION_2)] = LOCK_REGION_2
    data[OFFSET_REGION_3:OFFSET_REGION_3 + len(LOCK_REGION_3)] = LOCK_REGION_3

    return bytes(data)


def print_regions(data, label):
    """Print the three OBD-related regions."""
    print(f"\n{label}:")
    print(f"  0x080: {format_hex(data[OFFSET_REGION_1:OFFSET_REGION_1 + 16])}")
    print(f"  0x0A0: {format_hex(data[OFFSET_REGION_2:OFFSET_REGION_2 + 16])}")
    print(f"  0x0B0: {format_hex(data[OFFSET_REGION_3:OFFSET_REGION_3 + 7])}")


def main():
    parser = argparse.ArgumentParser(
        description='Porsche 986/996 ACU OBD Unlock Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Check if OBD is locked or unlocked
    python3 obd_unlock.py dump.bin --check

    # Unlock OBD access
    python3 obd_unlock.py locked.bin unlocked.bin

    # Lock OBD access (re-enable anti-theft)
    python3 obd_unlock.py unlocked.bin locked.bin --lock

Notes:
    - The unlock values are UNIVERSAL across all M534/M535 modules
    - Unlocking allows key programming via PIWIS/PST2/ABRITES over OBD-II
    - Locking restores the anti-theft protection
    - Always keep a backup of your original EEPROM!
        """
    )
    parser.add_argument('input', help='Input EEPROM dump file')
    parser.add_argument('output', nargs='?', help='Output EEPROM file (not needed with --check)')
    parser.add_argument('--lock', action='store_true', help='Lock OBD access (default is unlock)')
    parser.add_argument('--check', action='store_true', help='Only check current status, no modification')
    parser.add_argument('--force', '-f', action='store_true', help='Force operation despite warnings')

    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"Error: Input file '{args.input}' not found")
        sys.exit(1)

    # Read input file
    with open(args.input, 'rb') as f:
        data = f.read()

    print("=" * 60)
    print("PORSCHE 986/996 ACU OBD UNLOCK TOOL")
    print("=" * 60)
    print(f"Input: {args.input} ({len(data)} bytes)")

    # Verify EEPROM
    issues = verify_eeprom(data)
    if issues:
        print("\nWarnings:")
        for issue in issues:
            print(f"  - {issue}")
        if not args.force and not args.check:
            print("\nUse --force to proceed anyway")
            sys.exit(1)

    # Check current status
    status, reason = check_obd_status(data)
    print(f"\nCurrent Status: {status.upper()}")
    print(f"  {reason}")

    if args.check:
        print_regions(data, "Current OBD regions")
        print("\n" + "=" * 60)
        if status == 'unlocked':
            print("OBD programming access is ENABLED")
            print("You can program keys via PIWIS/PST2/ABRITES over OBD-II")
        elif status == 'locked':
            print("OBD programming access is DISABLED")
            print("Key programming via OBD-II will be rejected")
            print("Use this tool without --check to unlock")
        else:
            print("OBD status could not be determined")
        sys.exit(0)

    # Require output file for modification
    if not args.output:
        print("\nError: Output file required (or use --check to only check status)")
        sys.exit(1)

    print(f"Output: {args.output}")
    print(f"Action: {'LOCK' if args.lock else 'UNLOCK'}")
    print("=" * 60)

    # Show before state
    print_regions(data, "BEFORE")

    # Apply modification
    if args.lock:
        if status == 'locked':
            print("\nNote: EEPROM already appears to be locked")
        modified = lock_obd(data)
        action = "locked"
    else:
        if status == 'unlocked':
            print("\nNote: EEPROM already appears to be unlocked")
        modified = unlock_obd(data)
        action = "unlocked"

    # Show after state
    print_regions(modified, "AFTER")

    # Verify PIN wasn't affected
    pin1 = modified[0x1EE:0x1F1]
    pin2 = modified[0x1F7:0x1FA]
    print(f"\nPIN verification:")
    print(f"  0x1EE: {format_hex(pin1)}")
    print(f"  0x1F7: {format_hex(pin2)}")
    if pin1 == pin2:
        print("  ✓ PIN intact")
    else:
        print("  ⚠ WARNING: PIN mismatch!")

    # Write output
    with open(args.output, 'wb') as f:
        f.write(modified)

    print(f"\n✓ Modified EEPROM saved to: {args.output}")
    print(f"  File size: {len(modified)} bytes")

    print("\n" + "=" * 60)
    print(f"SUCCESS! OBD access is now {action.upper()}")
    print("=" * 60)

    if not args.lock:
        print("""
Next steps:
1. Flash the modified EEPROM back to your ACU
2. Reinstall ACU in car
3. Connect PIWIS/PST2/ABRITES via OBD-II
4. You should now be able to program keys with your PIN

To re-enable anti-theft protection later:
    python3 obd_unlock.py {output} relocked.bin --lock
""".format(output=args.output))
    else:
        print("""
OBD anti-theft protection has been restored.
Key programming via OBD-II will now be rejected.
""")


if __name__ == "__main__":
    main()
