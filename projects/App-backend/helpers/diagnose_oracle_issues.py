#!/usr/bin/env python3
"""
Comprehensive Oracle Diagnostics
"""
import os
import json
import requests
import base64
from algosdk.v2client import algod, indexer
from algosdk import mnemonic, account, encoding
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def diagnose_oracle_setup():
    """Comprehensive diagnosis of oracle setup issues"""

    print("🔍 Comprehensive Oracle Diagnostics")
    print("=" * 60)

    # Configuration
    oracle_mnemonic = os.getenv("ORACLE_MNEMONIC")
    app_id = int(os.getenv("APP_ID", "1039"))
    algod_token = os.getenv("ALGOD_TOKEN", "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
    algod_server = os.getenv("ALGOD_SERVER", "http://localhost")
    algod_port = int(os.getenv("ALGOD_PORT", "4001"))

    print("📋 Configuration Check:")
    print(f"   App ID: {app_id}")
    print(f"   Algod: {algod_server}:{algod_port}")
    print(f"   Oracle Mnemonic: {'✓ Set' if oracle_mnemonic else '✗ Missing'}")

    # 1. Check oracle account
    if oracle_mnemonic:
        try:
            oracle_private_key = mnemonic.to_private_key(oracle_mnemonic)
            oracle_address = account.address_from_private_key(oracle_private_key)
            print(f"   Oracle Address: {oracle_address}")
        except Exception as e:
            print(f"   ❌ Oracle Mnemonic Error: {e}")
            return
    else:
        print("   ❌ No oracle mnemonic configured")
        return

    # 2. Check Algod connection
    try:
        algod_client = algod.AlgodClient(algod_token, f"{algod_server}:{algod_port}")
        status = algod_client.status()
        print(f"   ✅ Algod Connected (Round: {status['last-round']})")
    except Exception as e:
        print(f"   ❌ Algod Connection Failed: {e}")
        print("   💡 Make sure LocalNet is running")
        return

    # 3. Check oracle balance
    try:
        account_info = algod_client.account_info(oracle_address)
        balance = account_info['amount'] / 1_000_000  # Convert to ALGO
        print(f"   💰 Oracle Balance: {balance} ALGO")
        if balance < 1:
            print("   ⚠️  Oracle balance low - may need funding")
    except Exception as e:
        print(f"   ❌ Could not check balance: {e}")

    # 4. Check smart contract
    try:
        app_info = algod_client.application_info(app_id)
        print("   ✅ Smart Contract Found")
    except Exception as e:
        print(f"   ❌ Smart Contract Not Found: {e}")
        return

    # 5. Check oracle authorization in contract
    try:
        global_state = app_info.get('params', {}).get('global-state', [])
        contract_oracle = None
        admin_address = None

        for state in global_state:
            if 'key' in state:
                key_b64 = state['key']
                try:
                    key_bytes = base64.b64decode(key_b64)
                    key = key_bytes.decode('utf-8')

                    value = state.get('value', {})
                    if value.get('type') == 1:  # Address type
                        addr_b64 = value.get('bytes', '')
                        addr_bytes = base64.b64decode(addr_b64)

                        if len(addr_bytes) == 32:
                            checksum = encoding.checksum(addr_bytes)
                            full_addr = addr_bytes + checksum
                            algorand_addr = encoding.encode_address(full_addr)

                            if key == 'oracle':
                                contract_oracle = algorand_addr
                            elif key == 'admin':
                                admin_address = algorand_addr

                except Exception as e:
                    # Try alternative decoding
                    if 'oracle' in str(state):
                        print(f"   ⚠️  Oracle state found but decode failed: {e}")

        print(f"   👑 Admin Address: {admin_address}")
        print(f"   🔮 Contract Oracle: {contract_oracle}")
        print(f"   🔑 Our Oracle: {oracle_address}")

        if contract_oracle == oracle_address:
            print("   ✅ Oracle correctly authorized in contract")
        else:
            print("   ❌ Oracle NOT authorized in contract")
            print(f"   Expected: {contract_oracle}")
            print(f"   Got: {oracle_address}")

    except Exception as e:
        print(f"   ❌ Could not check contract state: {e}")

    # 6. Test oracle endpoint
    print("\n🔮 Testing Oracle API:")
    test_data = {
        "policy_id": 1,
        "zip_code": "63017",
        "start_date": "2025-09-15",
        "end_date": "2026-10-14",
        "coverage_amount": "2.0",
        "direction": 1,
        "threshold": 50,
        "slope": 25,
        "fee_paid": 2000000,
        "settled": False,
        "owner": "EJO5V3L465WJRDYRL4CFYXBDA2QQ6QUHWJXL7IL3VJAJJ6G4ZXUOBBLIDI"
    }

    try:
        response = requests.post(
            "http://localhost:8000/oracle-settle",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )

        if response.status_code == 200:
            result = response.json()
            print("   ✅ API Response Received")
            print(f"   Decision: {'Approve' if result.get('decision') == 1 else 'Reject'}")
            print(f"   Transaction Success: {result.get('transaction_success')}")

            if not result.get('transaction_success'):
                print("   ❌ Transaction Failed - Check Logs Above")
                print("   🔍 Possible Issues:")
                print("      • Oracle not authorized in contract")
                print("      • Policy doesn't exist or already settled")
                print("      • Oracle account balance too low")
                print("      • Smart contract method call error")
            else:
                print("   🎉 SUCCESS: Real blockchain transaction!")
        else:
            print(f"   ❌ API Error: {response.status_code}")

    except requests.exceptions.RequestException as e:
        print(f"   ❌ API Request Failed: {e}")
        print("   💡 Make sure backend server is running")

    print("\n📋 Summary:")
    print("=" * 30)

    issues = []
    if contract_oracle != oracle_address:
        issues.append("Oracle not authorized in smart contract")
    if balance < 1:
        issues.append("Oracle account balance too low")
    if not result.get('transaction_success', False):
        issues.append("Blockchain transaction failing")

    if issues:
        print("❌ Issues Found:")
        for issue in issues:
            print(f"   • {issue}")
    else:
        print("✅ All systems operational!")

if __name__ == "__main__":
    diagnose_oracle_setup()
