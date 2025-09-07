#!/usr/bin/env python3
"""
Check Oracle Status and Configuration
"""
import os
from dotenv import load_dotenv

def check_oracle_status():
    """Check the current oracle configuration and status"""

    print("🌾 AgriGuard Oracle Status Check")
    print("=" * 40)

    # Load environment variables
    load_dotenv()

    # Check Google API Key
    google_api_key = os.getenv("GOOGLE_API_KEY", "")
    if not google_api_key or google_api_key == "your_gemini_api_key_here":
        print("❌ Google API Key: NOT CONFIGURED")
        print("   Using mock analysis")
    else:
        print("✅ Google API Key: CONFIGURED")
        print("   Using real Gemini AI analysis")

    # Check Algorand configuration
    app_id = os.getenv("APP_ID", "")
    oracle_mnemonic = os.getenv("ORACLE_MNEMONIC", "")

    if app_id:
        print(f"✅ Smart Contract ID: {app_id}")
    else:
        print("❌ Smart Contract ID: NOT CONFIGURED")

    if oracle_mnemonic and oracle_mnemonic != "YOUR_ORACLE_MNEMONIC_HERE":
        print("✅ Oracle Mnemonic: CONFIGURED")
    else:
        print("❌ Oracle Mnemonic: NOT CONFIGURED")

    # Check algokit_utils
    try:
        from algokit_utils import AlgorandClient
        print("✅ AlgoKit Utils: AVAILABLE")
        print("   Real smart contract calls enabled")
    except ImportError:
        print("❌ AlgoKit Utils: NOT AVAILABLE")
        print("   Using transaction simulation")

    print()
    print("📋 Current Oracle Capabilities:")
    print("- ✅ Mock analysis (always available)")
    print("- ✅ Transaction simulation (always available)")

    if google_api_key and google_api_key != "your_gemini_api_key_here":
        print("- ✅ Real Gemini AI analysis")
    else:
        print("- ❌ Real Gemini AI analysis (needs API key)")

    if app_id and oracle_mnemonic and oracle_mnemonic != "YOUR_ORACLE_MNEMONIC_HERE":
        try:
            from algokit_utils import AlgorandClient
            print("- ✅ Real smart contract calls")
        except ImportError:
            print("- ❌ Real smart contract calls (needs algokit-utils)")
    else:
        print("- ❌ Real smart contract calls (needs configuration)")

    print()
    print("🔧 To enable full functionality:")
    if not google_api_key or google_api_key == "your_gemini_api_key_here":
        print("1. Get Gemini API key from: https://makersuite.google.com/app/apikey")
        print("2. Update GOOGLE_API_KEY in .env file")

    if not oracle_mnemonic or oracle_mnemonic == "YOUR_ORACLE_MNEMONIC_HERE":
        print("3. Oracle account already created - mnemonic is in .env file")

    print("4. Install algokit-utils: pip install algokit-utils")
    print("5. Fund oracle account with ALGO from LocalNet dispenser")

if __name__ == "__main__":
    check_oracle_status()
