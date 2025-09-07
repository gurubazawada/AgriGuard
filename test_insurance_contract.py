"""
Comprehensive test file for AgriGuard Insurance Contract
Tests all functions that frontend and oracle would call
"""

import pytest
from algopy_testing import algopy_testing_context
from algopy import UInt64, Account, Address, String, DynamicBytes
from algopy.arc4 import UInt64 as ARC4UInt64

# Import the contract
from projects.App_contracts.smart_contracts.insurance.contract import AgriGuardInsurance
from projects.App_contracts.smart_contracts.insurance.abi_types import PolicyData


class TestAgriGuardInsurance:
    """Test suite for AgriGuard Insurance Contract"""
    
    def setup_method(self):
        """Set up test environment before each test"""
        self.context = algopy_testing_context()
        self.contract = AgriGuardInsurance()
        
        # Create test accounts
        self.admin = Account()
        self.user = Account()
        self.oracle = Account()
        
        # Initialize contract
        self.contract.create_application(Address.from_bytes(self.admin.bytes))
        self.contract.set_oracle(Address.from_bytes(self.oracle.bytes))
    
    def test_contract_initialization(self):
        """Test contract initialization"""
        # Check admin is set
        globals_data = self.contract.get_globals()
        assert globals_data[0].native == self.admin.native
        assert globals_data[1].native == self.oracle.native
        assert globals_data[2].native == 0  # pool_reserved
        assert globals_data[3].native == 2_000_000  # safety_buffer
        assert globals_data[4].native == 1  # next_policy_id
    
    def test_set_oracle(self):
        """Test setting oracle account"""
        new_oracle = Account()
        self.contract.set_oracle(Address.from_bytes(new_oracle.bytes))
        
        globals_data = self.contract.get_globals()
        assert globals_data[1].native == new_oracle.native
    
    def test_buy_policy_success(self):
        """Test successful policy purchase"""
        # Fund the contract first
        self.context.set_balance(self.contract.address, 10_000_000)  # 10 ALGO
        
        # Test parameters
        zip_code = DynamicBytes(b"90210")
        t0 = ARC4UInt64(1700000000)  # Start time
        t1 = ARC4UInt64(1702592000)  # End time (30 days later)
        cap = ARC4UInt64(1_000_000)  # 1 ALGO
        direction = ARC4UInt64(1)    # Trigger when < threshold
        threshold = ARC4UInt64(32)   # 32°F
        slope = ARC4UInt64(1000)     # Slope
        fee = ARC4UInt64(100_000)    # 0.1 ALGO fee
        
        # Set transaction sender
        self.context.set_sender(self.user)
        
        # Buy policy
        policy_id = self.contract.buy_policy(
            zip_code, t0, t1, cap, direction, threshold, slope, fee
        )
        
        # Verify policy was created
        assert policy_id.native == 1
        
        # Check policy details
        policy = self.contract.get_policy(policy_id)
        assert policy.owner.native == self.user.native
        assert policy.zip_code.bytes == b"90210"
        assert policy.t0.native == 1700000000
        assert policy.t1.native == 1702592000
        assert policy.cap.native == 1_000_000
        assert policy.direction.native == 1
        assert policy.threshold.native == 32
        assert policy.slope.native == 1000
        assert policy.fee_paid.native == 100_000
        assert policy.settled.native == 0
    
    def test_buy_policy_insufficient_payment(self):
        """Test policy purchase with insufficient payment"""
        # Don't fund the contract
        self.context.set_balance(self.contract.address, 50_000)  # Very low balance
        
        # Set transaction sender
        self.context.set_sender(self.user)
        
        # Try to buy policy
        with pytest.raises(Exception, match="Insufficient payment"):
            self.contract.buy_policy(
                DynamicBytes(b"90210"),
                ARC4UInt64(1700000000),
                ARC4UInt64(1702592000),
                ARC4UInt64(1_000_000),
                ARC4UInt64(1),
                ARC4UInt64(32),
                ARC4UInt64(1000),
                ARC4UInt64(100_000)
            )
    
    def test_buy_policy_validation_errors(self):
        """Test policy purchase validation errors"""
        # Fund the contract
        self.context.set_balance(self.contract.address, 10_000_000)
        self.context.set_sender(self.user)
        
        # Test invalid cap (too low)
        with pytest.raises(Exception, match="Policy cap too low"):
            self.contract.buy_policy(
                DynamicBytes(b"90210"),
                ARC4UInt64(1700000000),
                ARC4UInt64(1702592000),
                ARC4UInt64(500),  # Too low
                ARC4UInt64(1),
                ARC4UInt64(32),
                ARC4UInt64(1000),
                ARC4UInt64(100_000)
            )
        
        # Test invalid direction
        with pytest.raises(Exception, match="Invalid direction parameter"):
            self.contract.buy_policy(
                DynamicBytes(b"90210"),
                ARC4UInt64(1700000000),
                ARC4UInt64(1702592000),
                ARC4UInt64(1_000_000),
                ARC4UInt64(2),  # Invalid direction
                ARC4UInt64(32),
                ARC4UInt64(1000),
                ARC4UInt64(100_000)
            )
        
        # Test invalid threshold
        with pytest.raises(Exception, match="Threshold must be positive"):
            self.contract.buy_policy(
                DynamicBytes(b"90210"),
                ARC4UInt64(1700000000),
                ARC4UInt64(1702592000),
                ARC4UInt64(1_000_000),
                ARC4UInt64(1),
                ARC4UInt64(0),  # Invalid threshold
                ARC4UInt64(1000),
                ARC4UInt64(100_000)
            )
    
    def test_get_policies_by_owner(self):
        """Test getting policies by owner"""
        # Fund the contract
        self.context.set_balance(self.contract.address, 10_000_000)
        self.context.set_sender(self.user)
        
        # Create a policy
        policy_id = self.contract.buy_policy(
            DynamicBytes(b"90210"),
            ARC4UInt64(1700000000),
            ARC4UInt64(1702592000),
            ARC4UInt64(1_000_000),
            ARC4UInt64(1),
            ARC4UInt64(32),
            ARC4UInt64(1000),
            ARC4UInt64(100_000)
        )
        
        # Get user's policies
        user_policies = self.contract.get_policies_by_owner(Address.from_bytes(self.user.bytes))
        assert user_policies[0].native == 1  # count
        assert user_policies[1].native == 1  # first policy ID
    
    def test_get_policy_by_owner_and_index(self):
        """Test getting specific policy by owner and index"""
        # Fund the contract
        self.context.set_balance(self.contract.address, 10_000_000)
        self.context.set_sender(self.user)
        
        # Create a policy
        policy_id = self.contract.buy_policy(
            DynamicBytes(b"90210"),
            ARC4UInt64(1700000000),
            ARC4UInt64(1702592000),
            ARC4UInt64(1_000_000),
            ARC4UInt64(1),
            ARC4UInt64(32),
            ARC4UInt64(1000),
            ARC4UInt64(100_000)
        )
        
        # Get policy by index
        result = self.contract.get_policy_by_owner_and_index(
            Address.from_bytes(self.user.bytes),
            ARC4UInt64(0)  # First policy
        )
        
        assert result[0].native == 1  # policy_id
        assert result[1].owner.native == self.user.native
    
    def test_oracle_settle_approve(self):
        """Test oracle settlement with approval"""
        # Fund the contract
        self.context.set_balance(self.contract.address, 10_000_000)
        self.context.set_sender(self.user)
        
        # Create a policy
        policy_id = self.contract.buy_policy(
            DynamicBytes(b"90210"),
            ARC4UInt64(1700000000),
            ARC4UInt64(1702592000),
            ARC4UInt64(1_000_000),
            ARC4UInt64(1),
            ARC4UInt64(32),
            ARC4UInt64(1000),
            ARC4UInt64(100_000)
        )
        
        # Switch to oracle account
        self.context.set_sender(self.oracle)
        
        # Settle policy with approval
        payout = self.contract.oracle_settle(policy_id, ARC4UInt64(1))
        
        # Verify payout
        assert payout.native == 1_000_000  # Full cap amount
        
        # Check policy is settled
        policy = self.contract.get_policy(policy_id)
        assert policy.settled.native == 1
    
    def test_oracle_settle_reject(self):
        """Test oracle settlement with rejection"""
        # Fund the contract
        self.context.set_balance(self.contract.address, 10_000_000)
        self.context.set_sender(self.user)
        
        # Create a policy
        policy_id = self.contract.buy_policy(
            DynamicBytes(b"90210"),
            ARC4UInt64(1700000000),
            ARC4UInt64(1702592000),
            ARC4UInt64(1_000_000),
            ARC4UInt64(1),
            ARC4UInt64(32),
            ARC4UInt64(1000),
            ARC4UInt64(100_000)
        )
        
        # Switch to oracle account
        self.context.set_sender(self.oracle)
        
        # Settle policy with rejection
        payout = self.contract.oracle_settle(policy_id, ARC4UInt64(0))
        
        # Verify no payout
        assert payout.native == 0
        
        # Check policy is settled
        policy = self.contract.get_policy(policy_id)
        assert policy.settled.native == 1
    
    def test_oracle_settle_unauthorized(self):
        """Test oracle settlement by unauthorized account"""
        # Fund the contract
        self.context.set_balance(self.contract.address, 10_000_000)
        self.context.set_sender(self.user)
        
        # Create a policy
        policy_id = self.contract.buy_policy(
            DynamicBytes(b"90210"),
            ARC4UInt64(1700000000),
            ARC4UInt64(1702592000),
            ARC4UInt64(1_000_000),
            ARC4UInt64(1),
            ARC4UInt64(32),
            ARC4UInt64(1000),
            ARC4UInt64(100_000)
        )
        
        # Try to settle as user (not oracle)
        self.context.set_sender(self.user)
        
        with pytest.raises(Exception, match="Only oracle"):
            self.contract.oracle_settle(policy_id, ARC4UInt64(1))
    
    def test_oracle_settle_already_settled(self):
        """Test oracle settlement of already settled policy"""
        # Fund the contract
        self.context.set_balance(self.contract.address, 10_000_000)
        self.context.set_sender(self.user)
        
        # Create a policy
        policy_id = self.contract.buy_policy(
            DynamicBytes(b"90210"),
            ARC4UInt64(1700000000),
            ARC4UInt64(1702592000),
            ARC4UInt64(1_000_000),
            ARC4UInt64(1),
            ARC4UInt64(32),
            ARC4UInt64(1000),
            ARC4UInt64(100_000)
        )
        
        # Switch to oracle account
        self.context.set_sender(self.oracle)
        
        # Settle policy first time
        self.contract.oracle_settle(policy_id, ARC4UInt64(1))
        
        # Try to settle again
        with pytest.raises(Exception, match="Already settled"):
            self.contract.oracle_settle(policy_id, ARC4UInt64(1))
    
    def test_get_pool_status(self):
        """Test getting pool status"""
        # Fund the contract
        self.context.set_balance(self.contract.address, 10_000_000)
        
        # Get pool status
        pool_status = self.contract.get_pool_status()
        assert pool_status[0].native == 10_000_000  # app_balance
        assert pool_status[1].native == 0  # pool_reserved
        assert pool_status[2].native == 8_000_000  # available (balance - min_balance - safety_buffer)
    
    def test_admin_withdraw(self):
        """Test admin withdrawal"""
        # Fund the contract
        self.context.set_balance(self.contract.address, 10_000_000)
        self.context.set_sender(self.admin)
        
        # Withdraw funds
        self.contract.admin_withdraw(ARC4UInt64(1_000_000), Address.from_bytes(self.user.bytes))
        
        # Verify withdrawal (in real scenario, user balance would increase)
        # This is a simplified test - in practice you'd check the user's balance
    
    def test_admin_withdraw_unauthorized(self):
        """Test admin withdrawal by unauthorized account"""
        # Fund the contract
        self.context.set_balance(self.contract.address, 10_000_000)
        self.context.set_sender(self.user)
        
        # Try to withdraw as user (not admin)
        with pytest.raises(Exception, match="Only admin can withdraw"):
            self.contract.admin_withdraw(ARC4UInt64(1_000_000), Address.from_bytes(self.user.bytes))
    
    def test_complete_flow(self):
        """Test complete insurance flow: buy policy -> oracle settle"""
        # Fund the contract
        self.context.set_balance(self.contract.address, 10_000_000)
        
        # 1. User buys policy
        self.context.set_sender(self.user)
        policy_id = self.contract.buy_policy(
            DynamicBytes(b"90210"),
            ARC4UInt64(1700000000),
            ARC4UInt64(1702592000),
            ARC4UInt64(1_000_000),
            ARC4UInt64(1),
            ARC4UInt64(32),
            ARC4UInt64(1000),
            ARC4UInt64(100_000)
        )
        
        # Verify policy created
        assert policy_id.native == 1
        
        # 2. Check user's policies
        user_policies = self.contract.get_policies_by_owner(Address.from_bytes(self.user.bytes))
        assert user_policies[0].native == 1
        
        # 3. Oracle settles policy
        self.context.set_sender(self.oracle)
        payout = self.contract.oracle_settle(policy_id, ARC4UInt64(1))
        
        # Verify payout
        assert payout.native == 1_000_000
        
        # 4. Verify policy is settled
        policy = self.contract.get_policy(policy_id)
        assert policy.settled.native == 1
        
        # 5. Check pool status
        pool_status = self.contract.get_pool_status()
        assert pool_status[1].native == 0  # pool_reserved should be 0 after settlement
        
        print("✅ Complete flow test passed!")


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
