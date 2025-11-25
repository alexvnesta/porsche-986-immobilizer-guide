#!/usr/bin/env python3
"""
Porsche 986/996 ACU EEPROM Remote Programmer
Writes remote barcode codes directly into EEPROM dumps.

Usage:
    python3 program_remote.py <input.bin> <output.bin> <slot> <24-char-code>

Example:
    python3 program_remote.py my_eeprom.bin modified.bin 1 4013A989D14C232DBF06B7C5

The 24-character code comes from the barcode tag on your new remote PCB.
Each remote has a unique code that must be programmed to the ACU.

IMPORTANT - Byte Swapping:
    The 93LC66 EEPROM uses 16-bit word organization. This script automatically
    byte-swaps the code before writing so you can enter it exactly as shown
    on the barcode label.

    Barcode shows:     40 13 A9 89 D1 4C 23 2D BF 06 B7 C5
    Written to EEPROM: 13 40 89 A9 4C D1 2D 23 06 BF C5 B7

    Use --no-swap if your code is already in EEPROM format.

Repository: https://github.com/alexvnesta/porsche-986-immobilizer-guide
"""

import sys
import os
import argparse


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
    # Handle odd length (shouldn't happen with 12-byte codes)
    if len(data) % 2:
        result[-1] = data[-1]
    return bytes(result)


def parse_hex_code(hex_string):
    """
    Parse a 24-character hex string into 12 bytes.

    Accepts formats:
        40059050236E317F2918D821
        40 05 90 50 23 6E 31 7F 29 18 D8 21
        40-05-90-50-23-6E-31-7F-29-18-D8-21
    """
    # Remove spaces, dashes, colons, and other separators
    hex_clean = hex_string.replace(' ', '').replace('-', '').replace(':', '').replace('.', '').upper()

    if len(hex_clean) != 24:
        raise ValueError(
            f"Code must be exactly 24 hex characters (12 bytes).\n"
            f"Got {len(hex_clean)} characters: '{hex_clean}'"
        )

    # Validate all characters are hex
    try:
        return bytes.fromhex(hex_clean)
    except ValueError as e:
        raise ValueError(f"Invalid hex characters in code: {e}")


def get_slot_offset(slot_num):
    """
    Get the EEPROM offset for a given remote slot (1-4).
    
    Memory layout:
        Slot 1: 0x100-0x10B (12 bytes)
        Slot 2: 0x10C-0x117 (12 bytes)  
        Slot 3: 0x118-0x123 (12 bytes)
        Slot 4: 0x124-0x12F (12 bytes)
    """
    offsets = {
        1: 0x100,
        2: 0x10C,
        3: 0x118,
        4: 0x124,
    }
    
    if slot_num not in offsets:
        raise ValueError(f"Slot must be 1-4, got {slot_num}")
    
    return offsets[slot_num]


def verify_eeprom(data):
    """Verify the EEPROM data looks valid."""
    issues = []
    
    if len(data) != 512:
        issues.append(f"Size is {len(data)} bytes, expected 512")
    
    # Check for all zeros or all FFs (likely bad read)
    if all(b == 0x00 for b in data):
        issues.append("Data is all zeros - likely a bad read")
    if all(b == 0xFF for b in data):
        issues.append("Data is all 0xFF - likely erased or bad read")
    
    # Check PIN locations match
    if len(data) >= 0x1FA:
        pin1 = data[0x1EE:0x1F1]
        pin2 = data[0x1F7:0x1FA]
        if pin1 != pin2:
            issues.append("PIN codes at 0x1EE and 0x1F7 don't match")
    
    return issues


def program_remote(input_file, output_file, slot_num, hex_code, force=False, no_swap=False):
    """Program a remote code into an EEPROM dump."""

    # Parse the hex code
    remote_code = parse_hex_code(hex_code)

    # Read the input file
    with open(input_file, 'rb') as f:
        data = bytearray(f.read())

    # Verify EEPROM
    issues = verify_eeprom(data)
    if issues and not force:
        print("Warning: EEPROM verification warnings:")
        for issue in issues:
            print(f"  - {issue}")
        print("\nUse --force to proceed anyway")
        return False

    # Get slot offset
    offset = get_slot_offset(slot_num)

    print(f"Remote code from barcode: {' '.join(f'{b:02X}' for b in remote_code)}")

    # Byte-swap for 16-bit EEPROM format (unless --no-swap specified)
    if no_swap:
        swapped_code = remote_code
        print(f"Writing code as-is (--no-swap): {' '.join(f'{b:02X}' for b in swapped_code)}")
    else:
        swapped_code = swap_bytes(remote_code)
        print(f"Byte-swapped for EEPROM:  {' '.join(f'{b:02X}' for b in swapped_code)}")

    print(f"Writing to slot {slot_num} at offset 0x{offset:03X}")
    
    # Show before state
    print(f"\nBEFORE (0x{offset:03X}-0x{offset+15:03X}):")
    print(f"  {' '.join(f'{b:02X}' for b in data[offset:offset+16])}")
    
    # Check if slot already has data
    current_slot = data[offset:offset+12]
    unique_vals = set(current_slot)
    if not (unique_vals <= {0xFF, 0xB7, 0x06, 0x00}):
        print(f"\n⚠ WARNING: Slot {slot_num} already contains data!")
        print(f"  Current: {' '.join(f'{b:02X}' for b in current_slot)}")
        if not force:
            response = input("  Overwrite? (y/N): ")
            if response.lower() != 'y':
                print("Aborted.")
                return False
    
    # Write the 12-byte remote code (byte-swapped)
    data[offset:offset+12] = swapped_code
    
    # Show after state
    print(f"\nAFTER (0x{offset:03X}-0x{offset+15:03X}):")
    print(f"  {' '.join(f'{b:02X}' for b in data[offset:offset+16])}")
    
    # Verify PIN is still intact
    pin1 = data[0x1EE:0x1F1]
    pin2 = data[0x1F7:0x1FA]
    print(f"\nPIN verification:")
    print(f"  Location 0x1EE: {' '.join(f'{b:02X}' for b in pin1)}")
    print(f"  Location 0x1F7: {' '.join(f'{b:02X}' for b in pin2)}")
    if pin1 == pin2:
        print(f"  ✓ PIN intact")
    else:
        print(f"  ⚠ WARNING: PIN mismatch detected!")
    
    # Write output file
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

    # Program with spaces in code
    python3 program_remote.py original.bin modified.bin 1 "40 13 A9 89 D1 4C 23 2D BF 06 B7 C5"

    # Force overwrite existing slot
    python3 program_remote.py original.bin modified.bin 1 4013A989D14C232DBF06B7C5 --force

    # Skip byte-swap (if code is already in EEPROM format)
    python3 program_remote.py original.bin modified.bin 1 1340A989... --no-swap

Notes:
    - Enter the code exactly as shown on the barcode tag - it will be byte-swapped automatically
    - The 93LC66 uses 16-bit words, so each byte pair is reversed in the raw dump
    - Slot 1 is at offset 0x100, Slot 2 at 0x10C, Slot 3 at 0x118, Slot 4 at 0x124
    - Always keep a backup of your original EEPROM!
    - After modifying, flash the EEPROM back to your ACU using CH341A or similar
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
            print("SUCCESS! Next steps:")
            print("=" * 60)
            print("""
1. Verify the modified file:
   python3 eeprom_analyzer.py {output}

2. Flash the modified EEPROM back to your ACU:
   - Connect SOIC-8 clip to 93LC66 chip
   - Open {output} in AsProgrammer
   - Click "Write"
   - Click "Verify" to confirm

3. Reinstall ACU in car and test remote

4. If remote doesn't work immediately:
   - Press button 2-3 times to allow sync
   - Check antenna connections
   - Verify correct frequency (315 MHz USA, 433 MHz EU)
""".format(output=args.output))
        else:
            sys.exit(1)
            
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
