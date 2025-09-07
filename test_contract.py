import asyncio
from algokit_utils import AlgorandClient, ensure_funded
from algokit_utils.config import config

async def test_insurance_contract():
    # Initialize client
    algorand = AlgorandClient.from_environment()
    
    # Create test accounts
    print("Creating test accounts...")
    user_account = algorand.account.random()
    oracle_account = algorand.account.random()
    
    # Fund accounts
    await ensure_funded(algorand, user_account.address, 10_000_000)  # 10 ALGO
    await ensure_funded(algorand, oracle_account.address, 10_000_000)  # 10 ALGO
    
    print(f"User account: {user_account.address}")
    print(f"Oracle account: {oracle_account.address}")
    
    # Import the contract client
    from smart_contracts.artifacts.insurance.insurance_client import InsuranceClient
    
    # Deploy contract
    print("\nDeploying contract...")
    app_client = algorand.application_client(
        app_spec=InsuranceClient.app_spec,
        signer=user_account
    )
    
    # Create the app
    app_id, app_address, tx_id = app_client.create(
        method="create_application",
        args=[user_account.address]
    )
    
    print(f"Contract deployed - App ID: {app_id}, Address: {app_address}")
    
    # Set oracle
    print("\nSetting oracle...")
    app_client.call(
        method="set_oracle",
        args=[oracle_account.address]
    )
    
    # Fund the pool
    print("\nFunding the pool...")
    fund_tx = algorand.send.payment(
        sender=user_account.address,
        receiver=app_address,
        amount=5_000_000  # 5 ALGO
    )
    print(f"Pool funded with 5 ALGO - TX: {fund_tx.tx_id}")
    
    # Test buying a policy
    print("\nBuying a policy...")
    
    # First, send payment for the fee
    fee_amount = 100_000  # 0.1 ALGO fee
    payment_tx = algorand.send.payment(
        sender=user_account.address,
        receiver=app_address,
        amount=fee_amount
    )
    print(f"Payment sent - TX: {payment_tx.tx_id}")
    
    # Buy policy
    policy_id = app_client.call(
        method="buy_policy",
        args=[
            "90210",  # zip_code
            1700000000,  # t0 (start time)
            1702592000,  # t1 (end time - 30 days later)
            1_000_000,   # cap (1 ALGO)
            1,           # direction (trigger when < threshold)
            32,          # threshold (32°F)
            1000,        # slope
            fee_amount   # fee
        ]
    ).return_value
    
    print(f"Policy created - ID: {policy_id}")
    
    # Check policy details
    print("\nChecking policy details...")
    policy = app_client.call(
        method="get_policy",
        args=[policy_id]
    ).return_value
    
    print(f"Policy owner: {policy.owner}")
    print(f"Policy cap: {policy.cap}")
    print(f"Policy settled: {policy.settled}")
    
    # Check user's policies
    print("\nChecking user's policies...")
    user_policies = app_client.call(
        method="get_policies_by_owner",
        args=[user_account.address]
    ).return_value
    
    print(f"User has {user_policies[0]} policies")
    
    # Test oracle settlement (approve)
    print("\nTesting oracle settlement...")
    
    # Switch to oracle account
    oracle_client = algorand.application_client(
        app_id=app_id,
        signer=oracle_account
    )
    
    payout = oracle_client.call(
        method="oracle_settle",
        args=[policy_id, 1]  # 1 = approve
    ).return_value
    
    print(f"Oracle settled policy - Payout: {payout}")
    
    # Check final policy status
    final_policy = app_client.call(
        method="get_policy",
        args=[policy_id]
    ).return_value
    
    print(f"Final policy status - Settled: {final_policy.settled}")
    
    # Check pool status
    pool_status = app_client.call(
        method="get_pool_status"
    ).return_value
    
    print(f"Pool status - Balance: {pool_status[0]}, Reserved: {pool_status[1]}, Available: {pool_status[2]}")
    
    print("\n✅ All tests completed successfully!")

if __name__ == "__main__":
    asyncio.run(test_insurance_contract())
