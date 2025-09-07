"""
Deployment configuration for AgriGuard Dispute Resolution Contract
"""

import logging
import algokit_utils
from algopy.arc4 import Address

logger = logging.getLogger(__name__)


def deploy() -> None:
    """Deploy the dispute resolution contract"""
    from smart_contracts.artifacts.dispute.agri_guard_dispute_client import (
        AgriGuardDisputeClient,
        APP_SPEC,
    )

    # Get Algorand client and deployer account
    algorand = algokit_utils.AlgorandClient.from_environment()
    deployer = algorand.account.from_environment("DEPLOYER")
    
    logger.info(f"Deploying AgriGuard Dispute Resolution with account: {deployer.address}")

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
    typed_client = AgriGuardDisputeClient(app_client)

    logger.info(f"Deployed AgriGuard Dispute Resolution with ID: {app_client.app_id}")
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
    
    # Set insurance contract address (can be set later)
    try:
        response = typed_client.send.set_insurance_contract(
            contract_address=deployer.address  # Placeholder - set to actual insurance contract later
        )
        logger.info(f"Set insurance contract successfully: {response.tx_id}")
        
    except Exception as e:
        logger.warning(f"Could not set insurance contract: {e}")

    logger.info("AgriGuard Dispute Resolution deployment completed successfully!")


if __name__ == "__main__":
    deploy()
