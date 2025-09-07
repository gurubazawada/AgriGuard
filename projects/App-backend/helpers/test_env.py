#!/usr/bin/env python3
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

print("Environment variables loaded:")
print(f"ORACLE_MNEMONIC: {'SET' if os.getenv('ORACLE_MNEMONIC') else 'NOT SET'}")
print(f"APP_ID: {os.getenv('APP_ID')}")
print(f"ALGOD_SERVER: {os.getenv('ALGOD_SERVER')}")
print(f"ALGOD_PORT: {os.getenv('ALGOD_PORT')}")

# Test mnemonic
mnemonic = os.getenv('ORACLE_MNEMONIC')
if mnemonic:
    from algosdk import mnemonic, account
    try:
        private_key = mnemonic.to_private_key(mnemonic)
        address = account.address_from_private_key(private_key)
        print(f"Oracle address: {address}")
    except Exception as e:
        print(f"Mnemonic error: {e}")
else:
    print("No mnemonic found")
