#!/usr/bin/env python3
"""
Ultra-simple deployment script for AgriGuard contracts
"""
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'smart_contracts'))

from algokit_utils import AlgorandClient, AppClient
from artifacts.insurance.agri_guard_insurance_client import APP_SPEC as INSURANCE_SPEC
from artifacts.dispute.agri_guard_dispute_client import APP_SPEC as DISPUTE_SPEC

def deploy_insurance():
    print("🚀 Deploying Insurance Contract...")
    
    # Get client and account
    algorand = AlgorandClient.from_environment()
    account = algorand.account.localnet_dispenser()
    
    print(f"📱 Using account: {account.address}")
    print(f"💰 Balance: {algorand.account.get_information(account.address).amount}")
    
    # Create app client
    from algokit_utils import AppClient
    app_client = AppClient(
        app_spec=INSURANCE_SPEC,
        algorand_client=algorand,
        signer=account,
        sender=account.address,
        app_id=0
    )
    
    # Deploy
    result = app_client.create("create_application", account.address)
    
    print(f"✅ Insurance Contract Deployed!")
    print(f"   App ID: {app_client.app_id}")
    print(f"   Address: {app_client.app_address}")
    
    # Fund the app
    algorand.send.payment({
        "sender": account.address,
        "receiver": app_client.app_address, 
        "amount": 5_000_000  # 5 ALGO
    })
    print("💰 App funded with 5 ALGO")
    
    # Set oracle
    app_client.call("set_oracle", account.address)
    print("🔮 Oracle set to deployer account")
    
    return app_client.app_id, app_client.app_address

def deploy_dispute(insurance_app_id=None):
    print("\n🚀 Deploying Dispute Contract...")
    
    # Get client and account
    algorand = AlgorandClient.from_environment()
    account = algorand.account.localnet_dispenser()
    
    # Create app client  
    from algokit_utils import AppClient
    app_client = AppClient(
        app_spec=DISPUTE_SPEC,
        algorand_client=algorand,
        signer=account,
        sender=account.address,
        app_id=0
    )
    
    # Deploy
    result = app_client.create("create_application", account.address)
    
    print(f"✅ Dispute Contract Deployed!")
    print(f"   App ID: {app_client.app_id}")
    print(f"   Address: {app_client.app_address}")
    
    # Fund the app
    algorand.send.payment({
        "sender": account.address,
        "receiver": app_client.app_address,
        "amount": 5_000_000  # 5 ALGO
    })
    print("💰 App funded with 5 ALGO")
    
    return app_client.app_id, app_client.app_address

if __name__ == "__main__":
    try:
        # Deploy insurance first
        insurance_id, insurance_addr = deploy_insurance()
        
        # Deploy dispute
        dispute_id, dispute_addr = deploy_dispute(insurance_id)
        
        print(f"\n🎉 All contracts deployed successfully!")
        print(f"📋 Summary:")
        print(f"   Insurance: ID={insurance_id}, Address={insurance_addr}")
        print(f"   Dispute:   ID={dispute_id}, Address={dispute_addr}")
        
    except Exception as e:
        print(f"❌ Deployment failed: {e}")
        import traceback
        traceback.print_exc()
