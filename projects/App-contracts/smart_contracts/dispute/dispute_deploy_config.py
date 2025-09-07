"""
Deployment configuration for AgriGuard Dispute Resolution Contract
"""

from algokit_utils import (
    ApplicationClient,
    ApplicationSpecification,
    get_algod_config,
    get_indexer_config,
    get_localnet_default_account,
)
from algopy import Account
from algopy.arc4 import Address as ARC4Address


def deploy() -> None:
    """Deploy the dispute resolution contract"""
    # Get the contract specification
    spec = ApplicationSpecification.from_json("artifacts/dispute/AgriGuardDispute.arc56.json")
    
    # Get the default account for LocalNet
    creator = get_localnet_default_account()
    
    # Create the application client
    algod_config = get_algod_config("localnet")
    indexer_config = get_indexer_config("localnet")
    
    client = ApplicationClient(
        algod_config=algod_config,
        indexer_config=indexer_config,
        app_spec=spec,
        creator=creator,
    )
    
    # Deploy the application
    app_id, app_address, tx_id = client.create(
        "AgriGuard Dispute Resolution",
        "Dispute resolution for insurance claims",
        global_schema=spec.global_schema,
        local_schema=spec.local_schema,
    )
    
    print(f"Deployed AgriGuard Dispute Resolution with ID: {app_id}")
    print(f"Application address: {app_address}")
    print(f"Transaction ID: {tx_id}")
    
    # Initialize the application
    result = client.call("create_application", admin=creator.address)
    print(f"Dispute contract initialized: {result}")


if __name__ == "__main__":
    deploy()
