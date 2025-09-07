#!/usr/bin/env python3
"""
Debug policy data structure to understand settlement status
"""
import base64
from algosdk.v2client import algod

def debug_policy_data():
    """Debug the policy data structure and settlement status"""

    algod_client = algod.AlgodClient(
        'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
        'http://localhost:4001'
    )

    try:
        boxes = algod_client.application_boxes(1039)

        if boxes.get('boxes'):
            # Take the first box to analyze
            box = boxes['boxes'][0]
            box_name_b64 = box.get('name', '')
            box_name_bytes = base64.b64decode(box_name_b64)

            # Extract policy ID
            policy_id = int.from_bytes(box_name_bytes[:8], 'big')
            print(f"🔍 Analyzing Policy ID: {policy_id}")

            # Get the box data
            box_data_response = algod_client.application_box_by_name(1039, box_name_bytes)
            if 'value' in box_data_response:
                data_bytes = base64.b64decode(box_data_response['value'])
                print(f"📦 Raw box data length: {len(data_bytes)} bytes")
                print(f"📦 Raw box data (hex): {data_bytes.hex()}")
                print(f"📦 Raw box data (bytes): {list(data_bytes)}")

                # ARC4 UInt64 encoding analysis
                # ARC4 UInt64 uses variable-length encoding, typically 1-9 bytes
                # First byte indicates the encoding type and length

                if len(data_bytes) >= 1:
                    first_byte = data_bytes[0]
                    print(f"🔢 First byte: {first_byte} (0x{first_byte:02x})")

                    # ARC4 UInt64 encoding:
                    # - If < 0x80: value is the byte itself (0-127)
                    # - If >= 0x80: multi-byte encoding
                    if first_byte < 0x80:
                        print(f"   📊 ARC4 UInt64 value: {first_byte}")
                        if first_byte == 0:
                            print("   ✅ POLICY IS UNSETTLED")
                        elif first_byte == 1:
                            print("   ❌ POLICY IS ALREADY SETTLED")
                        else:
                            print(f"   ❓ UNEXPECTED SETTLED VALUE: {first_byte}")
                    else:
                        print("   🔄 Multi-byte ARC4 UInt64 encoding detected")

                        # For multi-byte, the value is encoded in subsequent bytes
                        # The number of bytes is determined by the first byte
                        length_indicator = first_byte & 0x7F
                        print(f"   📏 Length indicator: {length_indicator}")

                        if length_indicator <= len(data_bytes) - 1:
                            value_bytes = data_bytes[1:1+length_indicator]
                            value = int.from_bytes(value_bytes, 'big')
                            print(f"   📊 ARC4 UInt64 value: {value}")
                            if value == 0:
                                print("   ✅ POLICY IS UNSETTLED")
                            elif value == 1:
                                print("   ❌ POLICY IS ALREADY SETTLED")
                            else:
                                print(f"   ❓ UNEXPECTED SETTLED VALUE: {value}")
                        else:
                            print("   ❌ Invalid ARC4 encoding length")

                print("\n" + "="*50)

                # Let's also try to decode the entire policy data structure
                print("🔧 Attempting to decode full PolicyData structure...")

                # PolicyData fields in order:
                # owner (Address - 32 bytes)
                # zip_code (String - variable length)
                # t0 (ARC4UInt64)
                # t1 (ARC4UInt64)
                # cap (ARC4UInt64)
                # direction (ARC4UInt64)
                # threshold (ARC4UInt64)
                # slope (ARC4UInt64)
                # fee_paid (ARC4UInt64)
                # settled (ARC4UInt64)

                offset = 0

                # Owner (Address - should be 32 bytes + ARC4 encoding)
                if offset < len(data_bytes):
                    owner_byte = data_bytes[offset]
                    if owner_byte >= 0x80:
                        # Multi-byte ARC4 Address
                        addr_len = owner_byte & 0x7F
                        if offset + 1 + addr_len <= len(data_bytes):
                            owner_addr = data_bytes[offset + 1:offset + 1 + addr_len]
                            print(f"👤 Owner: {owner_addr.hex()}")
                            offset += 1 + addr_len
                        else:
                            print("❌ Invalid owner encoding")
                            return
                    else:
                        print("❌ Unexpected owner encoding")
                        return

                # Skip other fields and focus on settled field (last field)
                # For simplicity, let's just look at the end of the data
                if len(data_bytes) >= 10:  # At least some data
                    print(f"🔚 Last 10 bytes: {data_bytes[-10:].hex()}")

                    # The settled field should be near the end
                    # Let's try to find ARC4 UInt64 patterns at the end
                    for i in range(max(0, len(data_bytes) - 20), len(data_bytes)):
                        if i < len(data_bytes):
                            byte_val = data_bytes[i]
                            if byte_val < 0x80:
                                print(f"   Position {i}: Single-byte UInt64 = {byte_val}")
                            elif byte_val >= 0x80:
                                length = byte_val & 0x7F
                                if i + 1 + length <= len(data_bytes):
                                    val_bytes = data_bytes[i+1:i+1+length]
                                    val = int.from_bytes(val_bytes, 'big')
                                    print(f"   Position {i}: Multi-byte UInt64 = {val} (length: {length})")

        else:
            print("❌ No boxes found")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_policy_data()
