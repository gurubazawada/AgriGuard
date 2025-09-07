import logging

import algokit_utils
from algopy.arc4 import Address

logger = logging.getLogger(__name__)


def deploy() -> None:
    """Deploy the simplified AgriGuard MVP contract"""
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    from artifacts.insurance.agri_guard_insurance_client import (
        AgriGuardInsuranceClient,
        APP_SPEC,
    )

    # Get Algorand client and deployer account
    algorand = algokit_utils.AlgorandClient.from_environment()
    # Use LocalNet dispenser account
    deployer = algorand.account.localnet_dispenser()
    
    logger.info(f"Deploying AgriGuard MVP with account: {deployer.address}")

    # Create app factory
    app_factory = algokit_utils.AppFactory(
        algokit_utils.AppFactoryParams(
            algorand=algorand,
            app_spec=APP_SPEC,
            default_sender=deployer.address,
        )
    )

    # Step 1: Deploy bare application (without method call that creates boxes)
    app_client, result = app_factory.send.bare.create()

    logger.info(f"✅ Deployed bare AgriGuard MVP with ID: {app_client.app_id}")
    logger.info(f"📱 Application address: {app_client.app_address}")

    # Step 2: Fund the application immediately so it can create boxes
    logger.info("💰 Funding application for box creation...")
    algorand.send.payment(
        algokit_utils.PaymentParams(
            amount=algokit_utils.AlgoAmount.from_algo(10),  # 10 ALGO for min balance + safety buffer
            sender=deployer.address,
            receiver=app_client.app_address,
        )
    )
    logger.info("Application funded successfully")

    # Step 3: Now call create_application method to initialize state
    logger.info("🏗️ Initializing application state...")
    app_client.call("create_application", deployer.address)
    logger.info("Application state initialized")

    # Step 4: Bootstrap the boxes after the contract is funded and initialized
    logger.info("📦 Creating contract boxes...")
    app_client.call("bootstrap")
    logger.info("Boxes created successfully")
    
    # Wrap in typed client
    typed_client = AgriGuardInsuranceClient(app_client)
    
    # Set oracle to deployer for testing (can be changed later)
    try:
        response = typed_client.send.set_oracle(
            oracle=deployer.address
        )
        logger.info(f"Set oracle successfully: {response.tx_id}")
        
    except Exception as e:
        logger.warning(f"Could not set oracle: {e}")

    # Log final state
    try:
        globals_response = typed_client.send.get_globals()
        logger.info(f"Current global state: {globals_response.return_value}")
    except Exception as e:
        logger.warning(f"Could not fetch global state: {e}")

    logger.info("AgriGuard MVP deployment completed successfully!")


if __name__ == "__main__":
    deploy()