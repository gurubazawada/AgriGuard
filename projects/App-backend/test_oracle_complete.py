#!/usr/bin/env python3
"""
Complete Oracle Setup and Testing Script for AgriGuard
"""
import os
import json
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_oracle_setup():
    """Test the complete oracle setup"""

    print("🔮 AgriGuard Oracle Setup Test")
    print("=" * 40)

    # Check environment variables
    oracle_mnemonic = os.getenv("ORACLE_MNEMONIC")
    app_id = os.getenv("APP_ID")
    algod_server = os.getenv("ALGOD_SERVER", "http://localhost")
    algod_port = os.getenv("ALGOD_PORT", "4001")

    print(f"📋 Configuration:")
    print(f"   Oracle Mnemonic: {'✓ Set' if oracle_mnemonic else '✗ Missing'}")
    print(f"   App ID: {app_id}")
    print(f"   Algod Server: {algod_server}:{algod_port}")

    # Test oracle endpoint
    test_data = {
        "policy_id": 1,
        "zip_code": "63017",
        "start_date": "2025-09-15",
        "end_date": "2026-10-14",
        "coverage_amount": "2.0",
        "direction": 1,
        "threshold": 1500,
        "slope": 100,
        "fee_paid": 2000000,
        "settled": False,
        "owner": "EJO5V3L465WJRDYRL4CFYXBDA2QQ6QUHWJXL7IL3VJAJJ6G4ZXUOBBLIDI"
    }

    try:
        print("\n🔍 Testing Oracle Settlement Endpoint...")
        response = requests.post(
            "http://localhost:8000/oracle-settle",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )

        if response.status_code == 200:
            result = response.json()
            print("✅ Oracle endpoint responding")
            print(f"   Decision: {'Approve' if result.get('decision') == 1 else 'Reject'}")
            print(f"   Reasoning: {result.get('reasoning', 'N/A')[:50]}...")
            print(f"   Transaction Success: {result.get('transaction_success', False)}")
        else:
            print(f"❌ Oracle endpoint failed: {response.status_code}")
            print(f"   Response: {response.text}")

    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to backend: {e}")
        print("   Make sure the backend is running with: python -m uvicorn main:app --reload")

def main():
    """Main setup function"""
    print("🌾 AgriGuard Oracle Setup Complete!")
    print("=" * 40)
    print()

    print("✅ Oracle Account Created:")
    print("   Address: 5AGK2ZPPQNODZZP6MNEQCETLJY523ALLR2WGDWCNNHWTRF6YJOAHH6QPVU")
    print("   Mnemonic: Configured in .env file")
    print()

    print("📋 Required Manual Steps:")
    print("1. Start LocalNet (if not running):")
    print("   algokit localnet start")
    print()

    print("2. Fund Oracle Account:")
    print("   algokit localnet dispenser --address 5AGK2ZPPQNODZZP6MNEQCETLJY523ALLR2WGDWCNNHWTRF6YJOAHH6QPVU --amount 10")
    print()

    print("3. Set Oracle in Smart Contract (run once):")
    print("   # This needs to be done through the contract admin interface")
    print("   # The oracle address above needs to be set as the oracle for the smart contract")
    print()

    print("4. Start Backend Server:")
    print("   cd /Users/gurubazawada/Desktop/AgriGuard/App/projects/App-backend")
    print("   python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000")
    print()

    print("5. Test Oracle Functionality:")
    print("   python test_oracle_complete.py")
    print()

    # Run the test
    print("\n" + "=" * 40)
    test_oracle_setup()

if __name__ == "__main__":
    main()
