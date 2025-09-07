#!/usr/bin/env python3
"""
Simple deployment script for AgriGuard Insurance Contract
"""
import logging
import sys
import os

# Add the smart_contracts directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'smart_contracts'))

import algokit_utils
from artifacts.insurance.agri_guard_insurance_client import (
    AgriGuardInsuranceClient,
    APP_SPEC,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    try:
        # Get Algorand client and dispenser account  
        algorand = algokit_utils.AlgorandClient.from_environment()
        deployer = algorand.account.localnet_dispenser()
        
        logger.info(f"Deploying AgriGuard Insurance with account: {deployer.address}")
        
        # Create app client directly from deployer account
        app_client = algorand.client.get_app_client_by_id(
            app_spec=APP_SPEC,
            app_id=0,  # 0 means create new app
            sender=deployer.address,
            signer=deployer
        )
        
        # Deploy the application
        result = app_client.create(
            "create_application",
            deployer.address
        )
        
        # Wrap in typed client
        typed_client = AgriGuardInsuranceClient(app_client)
        
        logger.info(f"✅ Deployed AgriGuard Insurance with App ID: {app_client.app_id}")
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
        
        # Set oracle
        logger.info("🔮 Setting oracle...")
        typed_client.send.set_oracle(oracle=deployer.address)
        
        logger.info("🎉 Insurance contract deployment completed successfully!")
        print(f"\n📋 Deployment Summary:")
        print(f"   App ID: {app_client.app_id}")
        print(f"   Address: {app_client.app_address}")
        print(f"   Oracle: {deployer.address}")
        
        return app_client.app_id, app_client.app_address
        
    except Exception as e:
        logger.error(f"❌ Deployment failed: {e}")
        return None, None

if __name__ == "__main__":
    main()
