#!/usr/bin/env python3
"""
Check Oracle Setup Status - Funding and Smart Contract Configuration
"""
import os
from algosdk.v2client import algod, indexer
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_oracle_setup():
    """Check if oracle is properly set up"""

    print("🔍 Oracle Setup Status Check")
    print("=" * 50)

    # Get configuration
    oracle_mnemonic = os.getenv("ORACLE_MNEMONIC")
    app_id = int(os.getenv("APP_ID", "1039"))
    algod_server = os.getenv("ALGOD_SERVER", "http://localhost")
    algod_port = int(os.getenv("ALGOD_PORT", "4001"))
    algod_token = os.getenv("ALGOD_TOKEN", "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")

    if oracle_mnemonic:
        from algosdk import mnemonic, account
        oracle_private_key = mnemonic.to_private_key(oracle_mnemonic)
        oracle_address = account.address_from_private_key(oracle_private_key)
        print(f"✅ Oracle Address: {oracle_address}")
    else:
        print("❌ Oracle mnemonic not found")
        return

    # Check oracle account balance
    try:
        print("\n💰 Checking Oracle Account Balance...")
        algod_client = algod.AlgodClient(algod_token, f"{algod_server}:{algod_port}")
        account_info = algod_client.account_info(oracle_address)

        balance = account_info['amount'] / 1_000_000  # Convert microALGO to ALGO
        print(f"   Oracle Balance: {balance} ALGO")

        if balance > 1:
            print("   ✅ Oracle account is funded")
        else:
            print("   ❌ Oracle account needs funding")
            print(f"   💡 Fund with: algokit localnet dispenser --address {oracle_address} --amount 10")

    except Exception as e:
        print(f"   ❌ Could not check balance: {e}")
        print("   💡 Make sure LocalNet is running")

    # Check if oracle is set in smart contract
    try:
        print("\n🔗 Checking Smart Contract Oracle Configuration...")
        # Get application global state
        app_info = algod_client.application_info(app_id)
        global_state = app_info.get('params', {}).get('global-state', [])

        oracle_found = False
        for state_var in global_state:
            if 'key' in state_var:
                key = state_var['key']
                if key == 'oracle':  # Base64 encoded 'oracle'
                    value_info = state_var.get('value', {})
                    if value_info.get('type') == 1:  # Address type
                        stored_oracle = value_info.get('bytes', '')
                        if stored_oracle == oracle_address:
                            oracle_found = True
                            print("   ✅ Oracle correctly set in smart contract")
                        else:
                            print(f"   ⚠️  Different oracle set: {stored_oracle}")
                        break

        if not oracle_found:
            print("   ❌ Oracle not set in smart contract")
            print("   💡 Need to call set_oracle() method with admin account")

    except Exception as e:
        print(f"   ❌ Could not check smart contract: {e}")

    # Summary
    print("\n📋 Setup Summary:")
    print("=" * 30)

    issues = []
    if balance <= 1:
        issues.append("Oracle account not funded")
    if not oracle_found:
        issues.append("Oracle not set in smart contract")

    if issues:
        print("❌ Issues to fix:")
        for issue in issues:
            print(f"   • {issue}")
    else:
        print("✅ Oracle setup appears complete!")
        print("   🎉 Ready for settlement transactions")

if __name__ == "__main__":
    check_oracle_setup()
