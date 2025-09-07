#!/usr/bin/env python3
"""
Emergency deployment script using direct Algorand SDK
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'smart_contracts'))

from algokit_utils import AlgorandClient, PaymentParams, AlgoAmount
from algosdk.v2client.algod import AlgodClient
from algosdk.transaction import ApplicationCreateTxn, PaymentTxn, wait_for_confirmation
from algosdk.logic import get_application_address
import json
import base64

def deploy_contract(teal_approval_path, teal_clear_path, contract_name):
    print(f"🚀 Emergency deployment of {contract_name}...")
    
    # Get client and account
    algorand = AlgorandClient.from_environment()
    deployer = algorand.account.localnet_dispenser()
    algod_client = algorand.client.algod
    
    print(f"📱 Using deployer: {deployer.address}")
    print(f"💰 Balance: {algorand.account.get_information(deployer.address).amount}")
    
    # Read TEAL files
    with open(teal_approval_path, 'r') as f:
        approval_source = f.read()
    with open(teal_clear_path, 'r') as f:
        clear_source = f.read()
    
    # Compile TEAL
    approval_result = algod_client.compile(approval_source)
    approval_program = base64.b64decode(approval_result['result'])
    
    clear_result = algod_client.compile(clear_source)
    clear_program = base64.b64decode(clear_result['result'])
    
    # Get suggested params
    params = algod_client.suggested_params()
    
    # Create application
    create_txn = ApplicationCreateTxn(
        sender=deployer.address,
        sp=params,
        on_complete=0,  # NoOp
        approval_program=approval_program,
        clear_program=clear_program,
        global_schema={'num_uints': 10, 'num_byte_slices': 10},
        local_schema={'num_uints': 5, 'num_byte_slices': 5},
        app_args=[deployer.address.encode()],  # Pass admin as argument
    )
    
    # Sign and submit
    signed_txn = deployer.sign_transaction(create_txn)
    txid = algod_client.send_transaction(signed_txn)
    print(f"📤 Submitted creation transaction: {txid}")
    
    # Wait for confirmation
    result = wait_for_confirmation(algod_client, txid)
    app_id = result['application-index']
    app_address = get_application_address(app_id)
    
    print(f"✅ {contract_name} deployed!")
    print(f"   App ID: {app_id}")
    print(f"   Address: {app_address}")
    
    # Fund the application
    print(f"💰 Funding application...")
    algorand.send.payment(
        PaymentParams(
            sender=deployer.address,
            receiver=app_address,
            amount=AlgoAmount.from_algo(10)
        )
    )
    print(f"✅ Application funded with 10 ALGO")
    
    return app_id, app_address

def main():
    try:
        # Deploy Insurance
        insurance_id, insurance_addr = deploy_contract(
            'smart_contracts/artifacts/insurance/AgriGuardInsurance.approval.teal',
            'smart_contracts/artifacts/insurance/AgriGuardInsurance.clear.teal',
            'Insurance'
        )
        
        # Deploy Dispute
        dispute_id, dispute_addr = deploy_contract(
            'smart_contracts/artifacts/dispute/AgriGuardDispute.approval.teal', 
            'smart_contracts/artifacts/dispute/AgriGuardDispute.clear.teal',
            'Dispute'
        )
        
        print(f"\n🎉 ALL CONTRACTS DEPLOYED!")
        print(f"📋 Insurance: ID={insurance_id}, Address={insurance_addr}")
        print(f"📋 Dispute:   ID={dispute_id}, Address={dispute_addr}")
        
        # Save to file
        deployment_info = {
            'insurance': {'id': insurance_id, 'address': insurance_addr},
            'dispute': {'id': dispute_id, 'address': dispute_addr}
        }
        
        with open('deployment_info.json', 'w') as f:
            json.dump(deployment_info, f, indent=2)
        print(f"💾 Deployment info saved to deployment_info.json")
        
    except Exception as e:
        print(f"❌ Emergency deployment failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
