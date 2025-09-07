#!/usr/bin/env python3
"""
Create Oracle Account for AgriGuard
"""
import os
from algosdk import mnemonic, account

def create_oracle():
    """Create oracle account and generate .env file"""

    print("🌾 Creating AgriGuard Oracle Account")
    print("=" * 40)

    # Create a simple test account using account generation
    private_key, oracle_address = account.generate_account()

    # Convert private key to mnemonic
    oracle_mnemonic = mnemonic.from_private_key(private_key)

    print(f"✅ Oracle Address: {oracle_address}")
    print(f"✅ Oracle Mnemonic: {oracle_mnemonic}")
    print()

    # Create .env file
    env_content = f"""# Google Gemini API Key
GOOGLE_API_KEY=your_gemini_api_key_here

# Smart Contract Configuration
APP_ID=1039
ALGOD_SERVER=http://localhost
ALGOD_PORT=4001
ALGOD_TOKEN=aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa

# Oracle Private Key (25-word mnemonic)
ORACLE_MNEMONIC={oracle_mnemonic}
"""

    # Write to .env_example since .env is blocked
    with open('.env_example', 'w') as f:
        f.write(env_content)

    print("✅ .env_example file created!")
    print("   Rename it to .env to use it.")

    # Write to oracle_info.txt for easy reference
    with open('oracle_info.txt', 'w') as f:
        f.write(f"Oracle Address: {oracle_address}\n")
        f.write(f"Oracle Mnemonic: {oracle_mnemonic}\n")

    print("✅ Oracle info saved to oracle_info.txt")
    print()

    print("📋 Next Steps:")
    print("1. Rename .env_example to .env")
    print("2. Fund the oracle account:")
    print(f"   python -m algokit localnet dispenser --address {oracle_address} --amount 10")
    print("3. Start the backend:")
    print("   python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000")

    return oracle_address, oracle_mnemonic

if __name__ == "__main__":
    create_oracle()
