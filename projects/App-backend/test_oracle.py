#!/usr/bin/env python3
"""
Test Oracle Settlement without API Key
"""
import requests
import json

def test_oracle_mock():
    """Test the oracle with mock analysis (no API key needed)"""

    print("🌾 Testing AgriGuard Oracle (Mock Mode)")
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

    print("📤 Sending test request to oracle...")
    print(f"Policy ID: {test_data['policy_id']}")
    print(f"Location: {test_data['zip_code']}")
    print(f"Coverage: {test_data['coverage_amount']} ALGO")
    print()

    try:
        response = requests.post(
            "http://localhost:8000/oracle-settle",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )

        if response.status_code == 200:
            result = response.json()
            print("✅ Oracle Response:")
            print(f"Decision: {'APPROVED' if result['decision'] == 1 else 'REJECTED'}")
            print(f"Reasoning: {result['reasoning']}")
            print(f"Confidence: {result['confidence']}")
            print(f"Settlement Amount: {result['settlement_amount']} microALGOs")
            print(f"Transaction Success: {result['transaction_success']}")

            if result['decision'] == 1:
                print("🎉 Policy APPROVED for settlement!")
            else:
                print("❌ Policy REJECTED - no payout")

        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)

    except requests.exceptions.ConnectionError:
        print("❌ Error: Cannot connect to backend server")
        print("Make sure the backend is running:")
        print("python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000")

if __name__ == "__main__":
    test_oracle_mock()
