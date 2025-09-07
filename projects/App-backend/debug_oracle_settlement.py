#!/usr/bin/env python3
"""
Debug Oracle Settlement - Test actual smart contract interaction
"""
import os
import json
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def debug_oracle_settlement():
    """Debug the oracle settlement process step by step"""

    print("🔍 Oracle Settlement Debug")
    print("=" * 50)

    # Check environment variables
    oracle_mnemonic = os.getenv("ORACLE_MNEMONIC")
    app_id = os.getenv("APP_ID")
    algod_server = os.getenv("ALGOD_SERVER", "http://localhost")
    algod_port = os.getenv("ALGOD_PORT", "4001")
    algod_token = os.getenv("ALGOD_TOKEN", "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")

    print("📋 Environment Configuration:")
    print(f"   Oracle Mnemonic: {'✓ Set' if oracle_mnemonic else '✗ Missing'}")
    print(f"   App ID: {app_id}")
    print(f"   Algod Server: {algod_server}:{algod_port}")
    print(f"   Algod Token: {'✓ Set' if algod_token and algod_token != 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa' else '✗ Using default'}")

    # Test oracle account
    if oracle_mnemonic:
        from algosdk import mnemonic, account
        try:
            oracle_private_key = mnemonic.to_private_key(oracle_mnemonic)
            oracle_address = account.address_from_private_key(oracle_private_key)
            print(f"   Oracle Address: {oracle_address}")
        except Exception as e:
            print(f"   ❌ Oracle Mnemonic Error: {e}")
            return

    # Test LocalNet connection
    try:
        from algosdk.v2client import algod
        print("\n🔌 Testing Algod Connection...")
        algod_client = algod.AlgodClient(algod_token, f"{algod_server}:{algod_port}")
        status = algod_client.status()
        print(f"   ✅ Connected to LocalNet (Round: {status['last-round']})")
    except Exception as e:
        print(f"   ❌ Algod Connection Failed: {e}")
        print("   💡 Make sure LocalNet is running: algokit localnet start")
        return

    # Test with a policy that should trigger approval
    test_data = {
        "policy_id": 1,
        "zip_code": "63017",
        "start_date": "2025-09-15",
        "end_date": "2026-10-14",
        "coverage_amount": "2.0",
        "direction": 1,
        "threshold": 100,  # Low threshold to trigger approval
        "slope": 50,
        "fee_paid": 2000000,
        "settled": False,
        "owner": "EJO5V3L465WJRDYRL4CFYXBDA2QQ6QUHWJXL7IL3VJAJJ6G4ZXUOBBLIDI"
    }

    print("\n🔮 Testing Oracle Settlement API...")
    print(f"   Policy ID: {test_data['policy_id']}")
    print(f"   Threshold: {test_data['threshold']} (should trigger approval)")

    try:
        response = requests.post(
            "http://localhost:8000/oracle-settle",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )

        if response.status_code == 200:
            result = response.json()
            print("   ✅ API Response Received")
            print(f"   Decision: {'Approve' if result.get('decision') == 1 else 'Reject'}")
            print(f"   Transaction Success: {result.get('transaction_success', False)}")
            print(f"   Transaction ID: {result.get('transaction_id', 'N/A')}")

            if result.get('transaction_success') and result.get('transaction_id'):
                print(f"   🎉 SUCCESS: Transaction {result['transaction_id']} confirmed!")
            else:
                print("   ⚠️  Transaction not successful - check logs above")

        else:
            print(f"   ❌ API Error: {response.status_code}")
            print(f"   Response: {response.text}")

    except requests.exceptions.RequestException as e:
        print(f"   ❌ Request Failed: {e}")
        print("   💡 Make sure backend server is running:")
        print("      python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000")

    print("\n🔧 Troubleshooting Tips:")
    print("1. Check if oracle account is funded:")
    print(f"   algokit localnet dispenser --address {oracle_address} --amount 10")
    print("\n2. Check if oracle is set in smart contract")
    print("   (This needs to be done by contract admin)")
    print("\n3. Check backend server logs for detailed errors")
    print("\n4. Verify LocalNet is running and accessible")

if __name__ == "__main__":
    debug_oracle_settlement()
