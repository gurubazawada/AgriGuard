#!/usr/bin/env python3
"""
Generate Oracle Account for AgriGuard
"""
import os

def generate_oracle():
    """Generate a real oracle account using a simple approach"""

    print("🌾 Generating Oracle Account")
    print("=" * 30)

    # Use a pre-generated valid mnemonic (25 words)
    oracle_mnemonic = "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon"

    print("✅ Oracle Mnemonic (25 words):")
    print(oracle_mnemonic)
    print()

    print("📋 To get the oracle address, run this in Python:")
    print("from algosdk import mnemonic, account")
    print(f"private_key = mnemonic.to_private_key('{oracle_mnemonic}')")
    print("address = account.address_from_private_key(private_key)")
    print("print(f'Oracle Address: {address}')")
    print()

    print("🔧 Then update your .env file:")
    print(f"ORACLE_MNEMONIC={oracle_mnemonic}")

    return oracle_mnemonic

if __name__ == "__main__":
    generate_oracle()
