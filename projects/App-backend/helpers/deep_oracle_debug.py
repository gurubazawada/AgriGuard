#!/usr/bin/env python3
"""
Deep Oracle Debugging - Check all possible failure points
"""
import os
import json
import requests
import base64
from algosdk.v2client import algod
from algosdk import mnemonic, account, encoding
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_policy_exists(policy_id):
    """Check if a policy exists in the smart contract"""
    print(f"\n🔍 Checking Policy {policy_id}...")

    try:
        algod_client = algod.AlgodClient(
            'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
            'http://localhost:4001'
        )

        # Get application box (where policies are stored)
        app_id = 1039
        box_name = policy_id.to_bytes(8, 'big')  # Convert policy_id to bytes

        try:
            box_response = algod_client.application_box_by_name(app_id, box_name)
            print(f"   ✅ Policy {policy_id} exists")
            return True
        except Exception as e:
            if "not found" in str(e).lower():
                print(f"   ❌ Policy {policy_id} does not exist")
                return False
            else:
                print(f"   ⚠️  Could not check policy: {e}")
                return None

    except Exception as e:
        print(f"   ❌ Error checking policy: {e}")
        return None

def test_oracle_call():
    """Test the oracle call with detailed logging"""
    print("\n🔮 Testing Oracle Call...")

    # Test data
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
        "owner": "EJO5V3L465WJRDYRL4CFYXBDA2QQ6QUHWJXL7IL3VJAJ6G4ZXUOBBLIDI"
    }

    try:
        response = requests.post(
            "http://localhost:8000/oracle-settle",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=15
        )

        result = response.json()
        print(f"   API Status: {response.status_code}")
        print(f"   Decision: {'Approve' if result.get('decision') == 1 else 'Reject'}")
        print(f"   Transaction Success: {result.get('transaction_success')}")
        print(f"   Transaction ID: {result.get('transaction_id', 'None')}")

        return result

    except Exception as e:
        print(f"   ❌ Oracle call failed: {e}")
        return None

def main():
    """Main diagnostic function"""
    print("🔬 Deep Oracle Debugging")
    print("=" * 50)

    # Check policy existence
    policy_exists = check_policy_exists(1)

    # Test oracle call
    oracle_result = test_oracle_call()

    # Analyze results
    print("\n📊 Analysis:")
    print("=" * 30)

    if oracle_result:
        decision = oracle_result.get('decision')
        tx_success = oracle_result.get('transaction_success')
        tx_id = oracle_result.get('transaction_id')

        print(f"Oracle Decision: {'Approve' if decision == 1 else 'Reject'}")
        print(f"Transaction Success: {tx_success}")
        print(f"Transaction ID: {tx_id}")

        if decision == 1 and not tx_success:
            print("\n🚨 ISSUE IDENTIFIED:")
            print("Oracle approved the claim but transaction failed!")
            print("\nPossible causes:")
            print("• Policy doesn't exist in smart contract")
            print("• Policy is already settled")
            print("• Oracle account has insufficient ALGO for fees")
            print("• Smart contract method call error")
            print("• Transaction construction error")

            if policy_exists == False:
                print("• ✅ CONFIRMED: Policy does not exist")
            elif policy_exists == True:
                print("• Policy exists, checking other issues...")

                # Check oracle balance
                oracle_mnemonic = os.getenv('ORACLE_MNEMONIC')
                if oracle_mnemonic:
                    oracle_private_key = mnemonic.to_private_key(oracle_mnemonic)
                    oracle_address = account.address_from_private_key(oracle_private_key)

                    try:
                        algod_client = algod.AlgodClient(
                            'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
                            'http://localhost:4001'
                        )
                        account_info = algod_client.account_info(oracle_address)
                        balance = account_info['amount'] / 1_000_000
                        print(f"• Oracle Balance: {balance} ALGO")

                        if balance < 0.1:
                            print("• ❌ ISSUE: Oracle has insufficient ALGO for transaction fees")
                        else:
                            print("• ✅ Oracle has sufficient ALGO")
                    except Exception as e:
                        print(f"• ❌ Could not check balance: {e}")

        elif decision == 0 and tx_success:
            print("✅ Oracle correctly rejected claim (transaction successful)")
        elif decision == 1 and tx_success:
            print("🎉 SUCCESS: Oracle approved and transaction completed!")
        else:
            print("⚠️  Unexpected result combination")

    else:
        print("❌ Could not get oracle result")

    print("\n🔧 Recommended Actions:")
    print("1. Check if policy exists in smart contract")
    print("2. Verify oracle has sufficient ALGO (at least 0.1 ALGO)")
    print("3. Check backend server logs for detailed error messages")
    print("4. Try with a different policy ID if policy 1 doesn't exist")

if __name__ == "__main__":
    main()
