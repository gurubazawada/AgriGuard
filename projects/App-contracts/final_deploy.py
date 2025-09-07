#!/usr/bin/env python3
"""
Final deployment script for AgriGuard contracts using the exact same method as algokit
"""
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'smart_contracts'))

from algokit_utils import AlgorandClient, AppFactory, AppFactoryParams, AppFactoryCreateMethodCallParams
from artifacts.insurance.agri_guard_insurance_client import APP_SPEC as INSURANCE_SPEC, AgriGuardInsuranceClient
from artifacts.dispute.agri_guard_dispute_client import APP_SPEC as DISPUTE_SPEC, AgriGuardDisputeClient

def deploy_insurance():
    print("🚀 Deploying Insurance Contract...")
    
    # Get client and account
    algorand = AlgorandClient.from_environment()
    account = algorand.account.localnet_dispenser()
    
    print(f"📱 Using account: {account.address}")
    print(f"💰 Balance: {algorand.account.get_information(account.address).amount}")
    
    # Create app factory like the original deploy_config.py
    app_factory = AppFactory(
        AppFactoryParams(
            algorand=algorand,
            app_spec=INSURANCE_SPEC,
            default_sender=account.address,
        )
    )
    
    # Deploy using exact same method
    app_client, result = app_factory.send.create(
        AppFactoryCreateMethodCallParams(
            method="create_application",
            args=[account.address],
        )
    )
    
    # Wrap in typed client
    typed_client = AgriGuardInsuranceClient(app_client)
    
    print(f"✅ Insurance Contract Deployed!")
    print(f"   App ID: {app_client.app_id}")
    print(f"   Address: {app_client.app_address}")
    
    # Fund the app
    from algokit_utils import PaymentParams, AlgoAmount
    algorand.send.payment(
        PaymentParams(
            sender=account.address,
            receiver=app_client.app_address,
            amount=AlgoAmount.from_algo(5)
        )
    )
    print("💰 App funded with 5 ALGO")
    
    # Set oracle
    typed_client.send.set_oracle(oracle=account.address)
    print("🔮 Oracle set to deployer account")
    
    return app_client.app_id, app_client.app_address

def deploy_dispute(insurance_app_id=None):
    print("\n🚀 Deploying Dispute Contract...")
    
    # Get client and account
    algorand = AlgorandClient.from_environment()
    account = algorand.account.localnet_dispenser()
    
    # Create app factory
    app_factory = AppFactory(
        AppFactoryParams(
            algorand=algorand,
            app_spec=DISPUTE_SPEC,
            default_sender=account.address,
        )
    )
    
    # Deploy
    app_client, result = app_factory.send.create(
        AppFactoryCreateMethodCallParams(
            method="create_application",
            args=[account.address],
        )
    )
    
    # Wrap in typed client
    typed_client = AgriGuardDisputeClient(app_client)
    
    print(f"✅ Dispute Contract Deployed!")
    print(f"   App ID: {app_client.app_id}")
    print(f"   Address: {app_client.app_address}")
    
    # Fund the app
    from algokit_utils import PaymentParams, AlgoAmount
    algorand.send.payment(
        PaymentParams(
            sender=account.address,
            receiver=app_client.app_address,
            amount=AlgoAmount.from_algo(5)
        )
    )
    print("💰 App funded with 5 ALGO")
    
    # Link to insurance contract if provided
    if insurance_app_id:
        print(f"🔗 Linking to insurance contract...")
        # Use deployer address as placeholder since we don't have the actual insurance contract address
        typed_client.send.set_insurance_contract(contract_address=account.address)
    
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
        
        # Save deployment info
        with open("deployment_info.txt", "w") as f:
            f.write(f"Insurance Contract:\n")
            f.write(f"  App ID: {insurance_id}\n")
            f.write(f"  Address: {insurance_addr}\n")
            f.write(f"\nDispute Contract:\n")
            f.write(f"  App ID: {dispute_id}\n")
            f.write(f"  Address: {dispute_addr}\n")
        
        print(f"💾 Deployment info saved to deployment_info.txt")
        
    except Exception as e:
        print(f"❌ Deployment failed: {e}")
        import traceback
        traceback.print_exc()
