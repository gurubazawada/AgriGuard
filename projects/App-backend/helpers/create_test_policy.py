#!/usr/bin/env python3
"""
Create a test policy directly in the smart contract for oracle testing
"""
import os
from algosdk.v2client import algod
from algosdk import transaction, account, mnemonic
from algosdk.transaction import ApplicationCallTxn
import algosdk

def create_test_policy():
    """Create a test policy for oracle settlement testing"""

    # Oracle account (hardcoded for testing)
    oracle_mnemonic = "start ancient fury despair race stumble review foot file captain cotton grit subway fame strategy female deliver alter ghost reduce forum common riot abandon soft"
    oracle_private_key = mnemonic.to_private_key(oracle_mnemonic)
    oracle_address = account.address_from_private_key(oracle_private_key)

    # Setup Algod client
    algod_client = algod.AlgodClient(
        'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
        'http://localhost:4001'
    )

    print(f"🔧 Creating test policy with oracle account: {oracle_address}")

    # Test policy data
    zip_code = b"63017"  # As bytes
    t0 = 1758153600  # Unix timestamp
    t1 = 1771977600  # Unix timestamp
    cap = 2000000    # 2 ALGO
    direction = 1
    threshold = 50
    slope = 25
    fee_paid = 100000  # 0.1 ALGO

    # Get suggested params
    params = algod_client.suggested_params()

    # Create buy_policy transaction
    app_call_txn = ApplicationCallTxn(
        sender=oracle_address,
        sp=params,
        index=1039,  # App ID
        on_complete=algosdk.transaction.OnComplete.NoOpOC,
        app_args=[
            "buy_policy",  # Method name
            zip_code,      # zip_code as bytes
            t0,           # t0
            t1,           # t1
            cap,          # cap
            direction,    # direction
            threshold,    # threshold
            slope,        # slope
            fee_paid      # fee_paid
        ],
        foreign_apps=None,
        foreign_assets=None,
        accounts=None,
        note=b"Create test policy for oracle"
    )

    # Sign and send
    signed_txn = app_call_txn.sign(oracle_private_key)
    tx_id = algod_client.send_transaction(signed_txn)

    print(f"🔧 Transaction sent: {tx_id}")

    # Wait for confirmation
    confirmed_txn = algosdk.transaction.wait_for_confirmation(algod_client, tx_id, 4)
    print(f"🔧 Transaction confirmed in round: {confirmed_txn['confirmed-round']}")

    # Try to extract the policy ID from logs if available
    if 'logs' in confirmed_txn and confirmed_txn['logs']:
        print(f"🔧 Transaction logs: {confirmed_txn['logs']}")
        # The policy ID might be in the logs

    return tx_id

if __name__ == "__main__":
    create_test_policy()
