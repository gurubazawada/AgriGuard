import logging

import algokit_utils
from algopy.arc4 import Address

logger = logging.getLogger(__name__)


def deploy() -> None:
    """Deploy the simplified AgriGuard MVP contract"""
    from smart_contracts.artifacts.insurance.agri_guard_insurance_client import (
        AgriGuardInsuranceClient,
        APP_SPEC,
    )

    # Get Algorand client and deployer account
    algorand = algokit_utils.AlgorandClient.from_environment()
    deployer = algorand.account.from_environment("DEPLOYER")
    
    logger.info(f"Deploying AgriGuard MVP with account: {deployer.address}")

    # Create app factory
    app_factory = algokit_utils.AppFactory(
        algokit_utils.AppFactoryParams(
            algorand=algorand,
            app_spec=APP_SPEC,
            default_sender=deployer.address,
        )
    )

    # Deploy the application using create method call
    app_client, result = app_factory.send.create(
        algokit_utils.AppFactoryCreateMethodCallParams(
            method="create_application",
            args=[deployer.address],  # Pass the admin address directly
        )
    )
    
    # Wrap in typed client
    typed_client = AgriGuardInsuranceClient(app_client)

    logger.info(f"Deployed AgriGuard MVP with ID: {app_client.app_id}")
    logger.info(f"Application address: {app_client.app_address}")

    # Fund the application for minimum balance requirements
    logger.info("Funding application for minimum balance...")
    
    # Send initial funding for minimum balance + some buffer
    algorand.send.payment(
        algokit_utils.PaymentParams(
            amount=algokit_utils.AlgoAmount.from_algo(10),  # 10 ALGO for min balance + safety buffer
            sender=deployer.address,
            receiver=app_client.app_address,
        )
    )
    
    logger.info("Application funded successfully")
    
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
