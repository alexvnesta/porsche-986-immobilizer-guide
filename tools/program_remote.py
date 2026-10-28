#!/usr/bin/env python3
"""
Porsche 986/996 ACU EEPROM Remote Programmer
Writes remote barcode codes directly into EEPROM dumps with dual-bank mirroring.

Usage:
    python3 program_remote.py <input.bin> <output.bin> <slot> <24-char-code>

Example:
    python3 program_remote.py my_eeprom.bin modified.bin 1 4013A989D14C232DBF06B7C5

The 24-character code comes from the barcode tag on your new remote PCB.
Each remote has a unique code that must be programmed to the ACU.

Architecture Note (Dual-Bank Mirroring & Slot Offsets):
    Each remote slot occupies 30 bytes (0x1E) in the 93LC66 EEPROM:
        - Slot 1: 0x0E2 (Bank A: 0x0E2..0x0F6, Bank B: 0x0F7..0x0FF)
        - Slot 2: 0x100 (Bank A: 0x100..0x114, Bank B: 0x115..0x11D)
        - Slot 3: 0x11E (Bank A: 0x11E..0x132, Bank B: 0x133..0x13B)
        - Slot 4: 0x13C (Bank A: 0x13C..0x150, Bank B: 0x151..0x159)

    This script updates both Bank A and Bank B mirror (first 9 bytes) to preserve
    dual-bank redundancy and prevent rollback/corruption rejections.

Repository: https://github.com/alexvnesta/porsche-986-immobilizer-guide
"""

import sys
import os
import argparse

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass


def swap_bytes(data):
    """
    Swap adjacent byte pairs for 16-bit EEPROM format.

    The 93LC66 is a 16-bit organized EEPROM. When reading/writing codes,
    each byte pair needs to be swapped:
        Input:  40 13 A9 89 D1 4C ...
        Output: 13 40 89 A9 4C D1 ...
    """
    result = bytearray(len(data))
    for i in range(0, len(data) - 1, 2):
        result[i] = data[i + 1]
        result[i + 1] = data[i]
    if len(data) % 2:
        result[-1] = data[-1]
    return bytes(result)


def parse_hex_code(hex_string):
    """Parse a 24-character hex string into 12 bytes."""
    hex_clean = hex_string.replace(' ', '').replace('-', '').replace(':', '').replace('.', '').upper()
    if len(hex_clean) != 24:
        raise ValueError(
            f"Code must be exactly 24 hex characters (12 bytes).\n"
            f"Got {len(hex_clean)} characters: '{hex_clean}'"
        )
    try:
        return bytes.fromhex(hex_clean)
    except ValueError as e:
        raise ValueError(f"Invalid hex characters in code: {e}")


def get_slot_offsets(slot_num):
    """
    Get the EEPROM offsets for a given remote slot (1-4).
    Each remote slot spans 30 bytes:
        - Bank A (21 bytes): base .. base + 20
        - Bank B (9 bytes mirror): base + 21 .. base + 29
    """
    if slot_num not in [1, 2, 3, 4]:
        raise ValueError(f"Slot must be 1-4, got {slot_num}")

    base_a = 0x0E2 + (slot_num - 1) * 30
    base_b = base_a + 21
    return base_a, base_b


def verify_eeprom(data):
    """Verify the EEPROM data looks valid."""
    issues = []
    if len(data) != 512:
        issues.append(f"Size is {len(data)} bytes, expected 512")
    if all(b == 0x00 for b in data):
        issues.append("Data is all zeros - likely a bad read")
    if all(b == 0xFF for b in data):
        issues.append("Data is all 0xFF - likely erased or bad read")
    if len(data) >= 0x1FA:
        pin1 = data[0x1EE:0x1F1]
        pin2 = data[0x1F7:0x1FA]
        if pin1 != pin2:
            issues.append("PIN codes at 0x1EE and 0x1F7 don't match")
    return issues


def program_remote(input_file, output_file, slot_num, hex_code, force=False, no_swap=False):
    """Program a remote code into an EEPROM dump with Bank A and Bank B mirroring."""
    remote_code = parse_hex_code(hex_code)

    with open(input_file, 'rb') as f:
        data = bytearray(f.read())

    issues = verify_eeprom(data)
    if issues and not force:
        print("Warning: EEPROM verification warnings:")
        for issue in issues:
            print(f"  - {issue}")
        print("\nUse --force to proceed anyway")
        return False

    offset_a, offset_b = get_slot_offsets(slot_num)

    print(f"Remote code from barcode: {' '.join(f'{b:02X}' for b in remote_code)}")

    if no_swap:
        swapped_code = remote_code
        print(f"Writing code as-is (--no-swap): {' '.join(f'{b:02X}' for b in swapped_code)}")
    else:
        swapped_code = swap_bytes(remote_code)
        print(f"Byte-swapped for EEPROM:  {' '.join(f'{b:02X}' for b in swapped_code)}")

    print(f"Writing to slot {slot_num}: Bank A at 0x{offset_a:03X}, Bank B at 0x{offset_b:03X}")

    current_slot = data[offset_a:offset_a + 12]
    unique_vals = set(current_slot)
    if not (unique_vals <= {0xFF, 0xB7, 0x06, 0x00}):
        print(f"\n⚠ WARNING: Slot {slot_num} already contains programmed key data!")
        print(f"  Current: {' '.join(f'{b:02X}' for b in current_slot)}")
        if not force:
            response = input("  Overwrite? (y/N): ")
            if response.lower() != 'y':
                print("Aborted.")
                return False

    # Write 12 bytes to Bank A
    data[offset_a:offset_a + 12] = swapped_code

    # Write first 9 bytes mirror to Bank B
    data[offset_b:offset_b + 9] = swapped_code[:9]

    # Verify PIN is intact
    pin1 = data[0x1EE:0x1F1]
    pin2 = data[0x1F7:0x1FA]
    print("\nPIN verification:")
    print(f"  Location 0x1EE: {' '.join(f'{b:02X}' for b in pin1)}")
    print(f"  Location 0x1F7: {' '.join(f'{b:02X}' for b in pin2)}")
    if pin1 == pin2:
        print("  ✓ PIN intact")
    else:
        print("  ⚠ WARNING: PIN mismatch detected!")

    with open(output_file, 'wb') as f:
        f.write(data)

    print(f"\n✓ Modified EEPROM saved to: {output_file}")
    print(f"  File size: {len(data)} bytes")
    return True


def main():
    parser = argparse.ArgumentParser(
        description='Porsche 986/996 EEPROM Remote Programmer',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Program remote to slot 1 (code is auto byte-swapped)
    python3 program_remote.py original.bin modified.bin 1 4013A989D14C232DBF06B7C5

    # Force overwrite existing slot
    python3 program_remote.py original.bin modified.bin 1 4013A989D14C232DBF06B7C5 --force
        """
    )
    parser.add_argument('input', help='Input EEPROM dump file')
    parser.add_argument('output', help='Output EEPROM file')
    parser.add_argument('slot', type=int, choices=[1, 2, 3, 4], help='Remote slot (1-4)')
    parser.add_argument('code', help='24-character hex code from remote barcode')
    parser.add_argument('--force', '-f', action='store_true', help='Force operation, skip confirmations')
    parser.add_argument('--no-swap', action='store_true',
                        help='Do NOT byte-swap the code (use if code is already in EEPROM format)')

    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"Error: Input file '{args.input}' not found")
        sys.exit(1)

    print("=" * 60)
    print("PORSCHE 986/996 EEPROM REMOTE PROGRAMMER")
    print("=" * 60)
    print(f"Input:  {args.input}")
    print(f"Output: {args.output}")
    print(f"Slot:   {args.slot}")
    print(f"Code:   {args.code}")
    print("=" * 60)

    try:
        success = program_remote(args.input, args.output, args.slot, args.code, args.force, args.no_swap)
        if success:
            print("\n" + "=" * 60)
            print("SUCCESS! Verification:")
            print("=" * 60)
            print(f"Run: python3 tools/eeprom_analyzer.py {args.output}")
        else:
            sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
