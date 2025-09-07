#!/usr/bin/env python3
"""
Complete test suite for AgriGuard Insurance Contract
Using algorand-python-testing framework
"""

import pytest
from algopy_testing import algopy_testing_context
from algopy import UInt64, Account, Address, String, DynamicBytes
from algopy.arc4 import UInt64 as ARC4UInt64

# Import the contract
import sys
import os
sys.path.append('projects/App-contracts/smart_contracts')

from insurance.contract import AgriGuardInsurance
from insurance.abi_types import PolicyData


class TestAgriGuardInsurance:
    """Complete test suite for AgriGuard Insurance Contract"""
    
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


def run_tests():
    """Run all tests"""
    print("🧪 Running AgriGuard Insurance Contract Tests\n")
    
    # Run pytest
    result = pytest.main([
        "test_insurance_complete.py",
        "-v",
        "--tb=short",
        "--color=yes"
    ])
    
    if result == 0:
        print("\n✅ All tests passed!")
    else:
        print("\n❌ Some tests failed!")
    
    return result


if __name__ == "__main__":
    run_tests()
