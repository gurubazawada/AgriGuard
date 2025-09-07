#!/usr/bin/env python3
"""
Test Real Smart Contract Call
"""
import requests
import time

def test_real_contract():
    """Test the real smart contract call"""

    print("🚀 Testing Real Smart Contract Call")
    print("=" * 40)

    # Test data
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

    print("📤 Making oracle settlement request...")
    print(f"Policy ID: {test_data['policy_id']}")
    print(f"Decision expected: APPROVE")
    print()

    try:
        # Make the request
        start_time = time.time()
        response = requests.post(
            "http://localhost:8000/oracle-settle",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=30  # 30 second timeout for blockchain operations
        )
        end_time = time.time()

        print(".2f")
        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print("\n✅ Oracle Response:")
            print(f"Decision: {'APPROVED' if result['decision'] == 1 else 'REJECTED'}")
            print(f"Reasoning: {result['reasoning']}")
            print(f"Confidence: {result['confidence']}")
            print(f"Settlement Amount: {result['settlement_amount']} microALGOs")
            print(f"Transaction Success: {result['transaction_success']}")
            print(f"Transaction ID: {result.get('transaction_id', 'N/A')}")

            if 'error' in result:
                print(f"Error Details: {result['error']}")

            if result['transaction_success']:
                print("\n🎉 SUCCESS: Real smart contract call completed!")
            else:
                print("\n⚠️  WARNING: Transaction failed, fell back to simulation")
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)

    except requests.exceptions.Timeout:
        print("❌ Timeout: Smart contract call took too long")
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Cannot connect to backend")
        print("Make sure the backend is running:")
        print("python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000")
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")

if __name__ == "__main__":
    test_real_contract()
