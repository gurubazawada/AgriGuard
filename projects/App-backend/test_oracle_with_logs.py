#!/usr/bin/env python3
"""
Test Oracle Settlement with detailed logging
"""
import os
import json
import requests
import subprocess
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_oracle_with_logs():
    """Test oracle settlement and show backend logs"""

    print("🔮 Testing Oracle Settlement with Backend Logs")
    print("=" * 60)

    # Start backend server in background
    print("🚀 Starting backend server...")
    backend_process = subprocess.Popen([
        "python", "-m", "uvicorn", "main:app",
        "--reload", "--host", "0.0.0.0", "--port", "8000"
    ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

    # Wait for server to start
    print("⏳ Waiting for server to start...")
    time.sleep(3)

    try:
        # Test data that should trigger approval
        test_data = {
            "policy_id": 1,
            "zip_code": "63017",
            "start_date": "2025-09-15",
            "end_date": "2026-10-14",
            "coverage_amount": "2.0",
            "direction": 1,
            "threshold": 50,  # Very low threshold to ensure approval
            "slope": 25,
            "fee_paid": 2000000,
            "settled": False,
            "owner": "EJO5V3L465WJRDYRL4CFYXBDA2QQ6QUHWJXL7IL3VJAJJ6G4ZXUOBBLIDI"
        }

        print("📤 Making oracle settlement request...")
        print(f"   Policy ID: {test_data['policy_id']}")
        print(f"   Threshold: {test_data['threshold']} (should definitely approve)")

        response = requests.post(
            "http://localhost:8000/oracle-settle",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=15
        )

        print(f"\n📥 Response Status: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print("✅ Oracle Response:")
            print(f"   Decision: {result.get('decision')} ({'Approve' if result.get('decision') == 1 else 'Reject'})")
            print(f"   Transaction Success: {result.get('transaction_success')}")
            print(f"   Transaction ID: {result.get('transaction_id', 'None')}")
            print(f"   Settlement Amount: {result.get('settlement_amount', 0)}")

            if result.get('transaction_success'):
                print("🎉 SUCCESS: Real blockchain transaction completed!")
            else:
                print("⚠️  FAILURE: Transaction failed - check server logs above")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"Response: {response.text}")

    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
    finally:
        # Stop the backend server
        print("\n🛑 Stopping backend server...")
        backend_process.terminate()
        backend_process.wait()

if __name__ == "__main__":
    test_oracle_with_logs()
