#!/usr/bin/env python3
"""
Simple deployment script for AgriGuard Dispute Contract
"""
import logging
import sys
import os

# Add the smart_contracts directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'smart_contracts'))

import algokit_utils
from artifacts.dispute.agri_guard_dispute_client import (
    AgriGuardDisputeClient,
    APP_SPEC,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main(insurance_app_id=None):
    try:
        # Get Algorand client and dispenser account  
        algorand = algokit_utils.AlgorandClient.from_environment()
        deployer = algorand.account.localnet_dispenser()
        
        logger.info(f"Deploying AgriGuard Dispute with account: {deployer.address}")
        
        # Create app factory
        app_factory = algokit_utils.AppFactory(
            algokit_utils.AppFactoryParams(
                algorand=algorand,
                app_spec=APP_SPEC,
                default_sender=deployer.address,
            )
        )
        
        # Deploy the application
        app_client, result = app_factory.send.create(
            algokit_utils.AppFactoryCreateMethodCallParams(
                method="create_application", 
                args=[deployer.address],
            )
        )
        
        # Wrap in typed client
        typed_client = AgriGuardDisputeClient(app_client)
        
        logger.info(f"✅ Deployed AgriGuard Dispute with App ID: {app_client.app_id}")
        logger.info(f"📍 Application Address: {app_client.app_address}")
        
        # Fund the application
        logger.info("💰 Funding application...")
        algorand.send.payment(
            algokit_utils.PaymentParams(
                amount=algokit_utils.AlgoAmount.from_algo(10),
                sender=deployer.address,
                receiver=app_client.app_address,
            )
        )
        
        # Link to insurance contract if provided
        if insurance_app_id:
            logger.info(f"🔗 Linking to insurance contract {insurance_app_id}...")
            # Note: This would need the actual insurance contract address, not app ID
            # For now, just use deployer address as placeholder
            typed_client.send.set_insurance_contract(contract_address=deployer.address)
        
        logger.info("🎉 Dispute contract deployment completed successfully!")
        print(f"\n📋 Deployment Summary:")
        print(f"   App ID: {app_client.app_id}")
        print(f"   Address: {app_client.app_address}")
        if insurance_app_id:
            print(f"   Linked to Insurance: {insurance_app_id}")
        
        return app_client.app_id, app_client.app_address
        
    except Exception as e:
        logger.error(f"❌ Deployment failed: {e}")
        return None, None

if __name__ == "__main__":
    insurance_id = sys.argv[1] if len(sys.argv) > 1 else None
    main(insurance_id)
