#!/usr/bin/env python3
"""
Oracle Setup Script for AgriGuard
"""
import os
import secrets
from algosdk import mnemonic, account

def setup_oracle():
    """Set up the oracle account and generate necessary files"""

    print("🌾 AgriGuard Oracle Setup")
    print("=" * 30)

    # Generate oracle account
    print("\n🔑 Generating Oracle Account...")

    # Use a test mnemonic (in production, generate a real one)
    # For now, we'll skip the account generation and create a mock setup
    oracle_mnemonic = "YOUR_ORACLE_MNEMONIC_HERE"
    oracle_address = "YOUR_ORACLE_ADDRESS_HERE"

    print(f"✅ Oracle Address: {oracle_address}")
    print(f"✅ Oracle Mnemonic: {oracle_mnemonic}")

    # Create .env file
    print("\n📝 Creating .env file...")
    env_content = f"""# Google Gemini API Key
GOOGLE_API_KEY=your_gemini_api_key_here

# Smart Contract Configuration
APP_ID=1039
ALGOD_SERVER=http://localhost
ALGOD_PORT=4001
ALGOD_TOKEN=aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa

# Oracle Private Key (24-word mnemonic)
ORACLE_MNEMONIC={oracle_mnemonic}
"""

    with open('.env', 'w') as f:
        f.write(env_content)

    print("✅ .env file created with oracle configuration")

    # Create setup instructions
    print("\n📋 Next Steps:")
    print("1. Fund the oracle account with ALGO:")
    print(f"   python -m algokit localnet dispenser --address {oracle_address} --amount 10")
    print("\n2. Start the backend server:")
    print("   python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000")
    print("\n3. Test the oracle endpoint:")
    print("   curl -X POST 'http://localhost:8000/oracle-settle' -H 'Content-Type: application/json' -d '{\"policy_id\": 1, \"zip_code\": \"63017\", \"start_date\": \"2025-09-15\", \"end_date\": \"2026-10-14\", \"coverage_amount\": \"2.0\", \"direction\": 1, \"threshold\": 1500, \"slope\": 100, \"fee_paid\": 2000000, \"settled\": false, \"owner\": \"EJO5V3L465WJRDYRL4CFYXBDA2QQ6QUHWJXL7IL3VJAJJ6G4ZXUOBBLIDI\"}'")

    return oracle_address, oracle_mnemonic

if __name__ == "__main__":
    setup_oracle()
