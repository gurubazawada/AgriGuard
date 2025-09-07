#!/usr/bin/env python3
"""
Test proper ABI method calls to the smart contract
"""
import algosdk
from algosdk.v2client import algod
from algosdk.transaction import ApplicationCallTxn
from algosdk import account, mnemonic
import base64
import hashlib

def get_method_selector(method_signature):
    """Get the 4-byte method selector for a given method signature"""
    method_hash = hashlib.sha3_256(method_signature.encode()).digest()
    return method_hash[:4]

def test_abi_call():
    """Test proper ABI-encoded method call"""

    algod_client = algod.AlgodClient(
        'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
        'http://localhost:4001'
    )

    # Oracle account
    oracle_mnemonic = "start ancient fury despair race stumble review foot file captain cotton grit subway fame strategy female deliver alter ghost reduce forum common riot abandon soft"
    oracle_private_key = mnemonic.to_private_key(oracle_mnemonic)
    oracle_address = account.address_from_private_key(oracle_private_key)

    print(f"🔧 Testing ABI method call with oracle: {oracle_address}")

    # Method: get_globals() - should be simple
    method_sig = "get_globals()"
    method_selector = get_method_selector(method_sig)

    print(f"📋 Method: {method_sig}")
    print(f"🔢 Selector: {method_selector.hex()}")

    try:
        params = algod_client.suggested_params()

        # Create ABI-encoded method call
        app_call_txn = ApplicationCallTxn(
            sender=oracle_address,
            sp=params,
            index=1039,  # App ID
            on_complete=algosdk.transaction.OnComplete.NoOpOC,
            app_args=[method_selector],  # Just the method selector, no args for get_globals
            foreign_apps=None,
            foreign_assets=None,
            accounts=None,
            note=b"Test ABI call"
        )

        signed_txn = app_call_txn.sign(oracle_private_key)
        tx_id = algod_client.send_transaction(signed_txn)

        print(f"✅ Transaction sent: {tx_id}")

        # Wait for confirmation
        confirmed_txn = algosdk.transaction.wait_for_confirmation(algod_client, tx_id, 4)
        print(f"✅ Transaction confirmed in round: {confirmed_txn['confirmed-round']}")

        if 'logs' in confirmed_txn and confirmed_txn['logs']:
            print(f"📋 Logs: {confirmed_txn['logs']}")
        else:
            print("📋 No logs")

        return True

    except Exception as e:
        print(f"❌ ABI call failed: {e}")
        return False

def test_oracle_settle_abi():
    """Test oracle_settle with proper ABI encoding"""

    algod_client = algod.AlgodClient(
        'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
        'http://localhost:4001'
    )

    # Oracle account
    oracle_mnemonic = "start ancient fury despair race stumble review foot file captain cotton grit subway fame strategy female deliver alter ghost reduce forum common riot abandon soft"
    oracle_private_key = mnemonic.to_private_key(oracle_mnemonic)
    oracle_address = account.address_from_private_key(oracle_private_key)

    print(f"\n🔮 Testing oracle_settle ABI call")
    print(f"🔧 Oracle: {oracle_address}")

    # Method: oracle_settle(uint64,uint64)
    method_sig = "oracle_settle(uint64,uint64)"
    method_selector = get_method_selector(method_sig)

    # Arguments
    policy_id = 8101813454558029171
    decision = 1  # Approve

    print(f"📋 Method: {method_sig}")
    print(f"🔢 Selector: {method_selector.hex()}")
    print(f"📊 Policy ID: {policy_id}, Decision: {decision}")

    try:
        params = algod_client.suggested_params()

        # Create ABI-encoded method call with arguments
        app_call_txn = ApplicationCallTxn(
            sender=oracle_address,
            sp=params,
            index=1039,  # App ID
            on_complete=algosdk.transaction.OnComplete.NoOpOC,
            app_args=[
                method_selector,  # Method selector
                policy_id,        # policy_id (uint64)
                decision          # approved (uint64)
            ],
            foreign_apps=None,
            foreign_assets=None,
            accounts=None,
            note=b"Oracle settle ABI test"
        )

        signed_txn = app_call_txn.sign(oracle_private_key)
        tx_id = algod_client.send_transaction(signed_txn)

        print(f"✅ Oracle settle transaction sent: {tx_id}")

        # Wait for confirmation
        confirmed_txn = algosdk.transaction.wait_for_confirmation(algod_client, tx_id, 4)
        print(f"✅ Transaction confirmed in round: {confirmed_txn['confirmed-round']}")

        if 'logs' in confirmed_txn and confirmed_txn['logs']:
            print(f"📋 Logs: {confirmed_txn['logs']}")
        else:
            print("📋 No logs")

        return True

    except Exception as e:
        print(f"❌ Oracle settle ABI call failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing ABI Method Calls")
    print("=" * 50)

    # Test simple method first
    success1 = test_abi_call()

    # Then test oracle_settle
    success2 = test_oracle_settle_abi()

    print("\n" + "=" * 50)
    if success1 and success2:
        print("✅ All ABI tests passed!")
    else:
        print("❌ Some ABI tests failed")
