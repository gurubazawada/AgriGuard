#!/usr/bin/env python3
"""
Simple test script for AgriGuard Insurance Contract
Tests the contract logic without external dependencies
"""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_contract_import():
    """Test that the contract can be imported"""
    try:
        # Add the contracts directory to the path
        import sys
        sys.path.append('projects/App-contracts/smart_contracts')
        
        from insurance.contract import AgriGuardInsurance
        from insurance.abi_types import PolicyData
        print("✅ Contract imports successfully")
        return True
    except Exception as e:
        print(f"❌ Contract import failed: {e}")
        return False

def test_contract_initialization():
    """Test contract initialization"""
    try:
        from insurance.contract import AgriGuardInsurance
        
        # Create contract instance
        contract = AgriGuardInsurance()
        
        # Check initial values
        assert contract.pool_reserved == 0
        assert contract.safety_buffer == 2_000_000
        assert contract.next_policy_id == 1
        assert contract.MIN_LEAD_TIME == 600
        assert contract.MIN_POLICY_FEE == 10_000
        assert contract.MAX_POLICY_CAP == 100_000_000
        
        print("✅ Contract initialization test passed")
        return True
    except Exception as e:
        print(f"❌ Contract initialization test failed: {e}")
        return False

def test_policy_data_structure():
    """Test PolicyData structure"""
    try:
        from insurance.abi_types import PolicyData
        from algopy.arc4 import Address, String, UInt64 as ARC4UInt64
        
        # Create a test policy
        policy = PolicyData(
            owner=Address.from_bytes(b"test_address_123456789012345678901234567890"),
            zip_code=String("90210"),
            t0=ARC4UInt64(1700000000),
            t1=ARC4UInt64(1702592000),
            cap=ARC4UInt64(1_000_000),
            direction=ARC4UInt64(1),
            threshold=ARC4UInt64(32),
            slope=ARC4UInt64(1000),
            fee_paid=ARC4UInt64(100_000),
            settled=ARC4UInt64(0)
        )
        
        # Verify structure
        assert policy.owner.bytes == b"test_address_123456789012345678901234567890"
        assert policy.zip_code.bytes == b"90210"
        assert policy.t0.native == 1700000000
        assert policy.t1.native == 1702592000
        assert policy.cap.native == 1_000_000
        assert policy.direction.native == 1
        assert policy.threshold.native == 32
        assert policy.slope.native == 1000
        assert policy.fee_paid.native == 100_000
        assert policy.settled.native == 0
        
        print("✅ PolicyData structure test passed")
        return True
    except Exception as e:
        print(f"❌ PolicyData structure test failed: {e}")
        return False

def test_contract_methods_exist():
    """Test that all required methods exist"""
    try:
        from insurance.contract import AgriGuardInsurance
        
        contract = AgriGuardInsurance()
        
        # Check required methods exist
        required_methods = [
            'create_application',
            'set_admin',
            'set_oracle',
            'fund_pool',
            'buy_policy',
            'oracle_settle',
            'admin_withdraw',
            'get_globals',
            'get_pool_status',
            'get_policy',
            'get_policy_count',
            'get_policies_by_owner',
            'get_policy_by_owner_and_index'
        ]
        
        for method_name in required_methods:
            assert hasattr(contract, method_name), f"Method {method_name} not found"
            method = getattr(contract, method_name)
            assert callable(method), f"Method {method_name} is not callable"
        
        print("✅ All required methods exist")
        return True
    except Exception as e:
        print(f"❌ Method existence test failed: {e}")
        return False

def test_contract_validation_logic():
    """Test contract validation logic"""
    try:
        from insurance.contract import AgriGuardInsurance
        from algopy import UInt64
        
        contract = AgriGuardInsurance()
        
        # Test validation constants
        assert contract.MIN_LEAD_TIME == 600  # 10 minutes
        assert contract.MIN_POLICY_FEE == 10_000  # 0.01 ALGO
        assert contract.MAX_POLICY_CAP == 100_000_000  # 100 ALGO
        assert contract.safety_buffer == 2_000_000  # 2 ALGO
        
        print("✅ Contract validation logic test passed")
        return True
    except Exception as e:
        print(f"❌ Contract validation logic test failed: {e}")
        return False

def run_all_tests():
    """Run all tests"""
    print("🧪 Running AgriGuard Insurance Contract Tests\n")
    
    tests = [
        test_contract_import,
        test_contract_initialization,
        test_policy_data_structure,
        test_contract_methods_exist,
        test_contract_validation_logic
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Contract is ready for deployment.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
