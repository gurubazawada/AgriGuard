#!/usr/bin/env python3
"""
Debug Smart Contract Call
"""
import os
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Configuration
APP_ID = int(os.getenv("APP_ID", "1039"))
ALGOD_SERVER = os.getenv("ALGOD_SERVER", "http://localhost")
ALGOD_PORT = int(os.getenv("ALGOD_PORT", "4001"))
ALGOD_TOKEN = os.getenv("ALGOD_TOKEN", "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
ORACLE_MNEMONIC = os.getenv("ORACLE_MNEMONIC", "")

def debug_contract_call():
    """Debug the smart contract call"""

    print("🔧 Debugging Smart Contract Call")
    print("=" * 40)

    try:
        import algosdk
        from algosdk import mnemonic, account
        from algosdk.v2client import algod
        from algosdk.transaction import ApplicationCallTxn

        print("✅ Imports successful")

        # Check configuration
        print(f"APP_ID: {APP_ID}")
        print(f"ALGOD_SERVER: {ALGOD_SERVER}")
        print(f"ALGOD_PORT: {ALGOD_PORT}")
        print(f"ORACLE_MNEMONIC configured: {'YES' if ORACLE_MNEMONIC else 'NO'}")

        if not ORACLE_MNEMONIC:
            print("❌ Oracle mnemonic not configured")
            return

        # Set up oracle account
        oracle_private_key = mnemonic.to_private_key(ORACLE_MNEMONIC)
        oracle_address = account.address_from_private_key(oracle_private_key)
        print(f"Oracle Address: {oracle_address}")

        # Set up Algod client
        algod_client = algod.AlgodClient(ALGOD_TOKEN, f"{ALGOD_SERVER}:{ALGOD_PORT}")
        print("✅ Algod client created")

        # Test connection
        status = algod_client.status()
        print(f"✅ Algod connection successful. Last round: {status['last-round']}")

        # Test contract info
        try:
            app_info = algod_client.application_info(APP_ID)
            print(f"✅ Contract {APP_ID} found")
            print(f"Creator: {app_info['params']['creator']}")
        except Exception as e:
            print(f"❌ Contract {APP_ID} not found: {e}")
            return

        # Get suggested params
        params = algod_client.suggested_params()
        print("✅ Suggested params obtained")

        # Create test transaction (without sending)
        app_call_txn = ApplicationCallTxn(
            sender=oracle_address,
            sp=params,
            index=APP_ID,
            on_complete=algosdk.transaction.OnComplete.NoOpOC,
            app_args=[],  # Empty args for testing
            foreign_apps=None,
            foreign_assets=None,
            accounts=None,
            note=b"Debug test"
        )
        print("✅ Transaction created successfully")

        print("\n🎯 All components working! Smart contract call should work.")

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_contract_call()
