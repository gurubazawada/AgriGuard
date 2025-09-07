#!/usr/bin/env python3
"""
Contract verification script
Verifies the contract structure and logic without running actual tests
"""

import os
import re

def verify_contract_structure():
    """Verify the contract file structure and content"""
    print("🔍 Verifying AgriGuard Insurance Contract Structure\n")
    
    contract_path = "projects/App-contracts/smart_contracts/insurance/contract.py"
    abi_types_path = "projects/App-contracts/smart_contracts/insurance/abi_types.py"
    
    # Check if files exist
    if not os.path.exists(contract_path):
        print(f"❌ Contract file not found: {contract_path}")
        return False
    
    if not os.path.exists(abi_types_path):
        print(f"❌ ABI types file not found: {abi_types_path}")
        return False
    
    print("✅ Contract files exist")
    
    # Read contract file
    with open(contract_path, 'r') as f:
        contract_content = f.read()
    
    with open(abi_types_path, 'r') as f:
        abi_types_content = f.read()
    
    # Check required imports
    required_imports = [
        'ARC4Contract',
        'UInt64',
        'Account',
        'BoxMap',
        'Global',
        'Txn',
        'subroutine',
        'itxn',
        'TransactionType',
        'urange'
    ]
    
    for import_name in required_imports:
        if import_name not in contract_content:
            print(f"❌ Missing import: {import_name}")
            return False
    
    print("✅ All required imports present")
    
    # Check required methods
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
    
    for method in required_methods:
        if f'def {method}(' not in contract_content:
            print(f"❌ Missing method: {method}")
            return False
    
    print("✅ All required methods present")
    
    # Check PolicyData structure
    if 'class PolicyData' not in abi_types_content:
        print("❌ PolicyData class not found")
        return False
    
    required_fields = [
        'owner: Address',
        'zip_code: String',
        't0: ARC4UInt64',
        't1: ARC4UInt64',
        'cap: ARC4UInt64',
        'direction: ARC4UInt64',
        'threshold: ARC4UInt64',
        'slope: ARC4UInt64',
        'fee_paid: ARC4UInt64',
        'settled: ARC4UInt64'
    ]
    
    for field in required_fields:
        if field not in abi_types_content:
            print(f"❌ Missing PolicyData field: {field}")
            return False
    
    print("✅ PolicyData structure complete")
    
    # Check buy_policy method has fee parameter
    if 'fee: ARC4UInt64' not in contract_content:
        print("❌ buy_policy method missing fee parameter")
        return False
    
    print("✅ buy_policy method has fee parameter")
    
    # Check validation logic
    validation_checks = [
        'Policy cap too low',
        'Policy cap too high',
        'Invalid direction parameter',
        'Threshold must be positive',
        'Slope must be positive',
        'Fee too low',
        'Insufficient payment',
        'Insufficient pool funds'
    ]
    
    for check in validation_checks:
        if check not in contract_content:
            print(f"❌ Missing validation: {check}")
            return False
    
    print("✅ All validation checks present")
    
    # Check oracle settlement logic
    if 'Only oracle' not in contract_content:
        print("❌ Missing oracle authorization check")
        return False
    
    if 'Already settled' not in contract_content:
        print("❌ Missing already settled check")
        return False
    
    print("✅ Oracle settlement logic complete")
    
    # Check payment logic
    if 'itxn.Payment(' not in contract_content:
        print("❌ Missing payment transaction logic")
        return False
    
    print("✅ Payment logic present")
    
    return True

def verify_contract_flow():
    """Verify the contract supports the complete flow"""
    print("\n🔄 Verifying Contract Flow Support\n")
    
    contract_path = "projects/App-contracts/smart_contracts/insurance/contract.py"
    
    with open(contract_path, 'r') as f:
        content = f.read()
    
    # Check flow components
    flow_components = [
        # 1. Contract initialization
        'create_application',
        'set_oracle',
        
        # 2. Policy purchase
        'buy_policy',
        'get_policies_by_owner',
        'get_policy',
        
        # 3. Oracle settlement
        'oracle_settle',
        
        # 4. Admin functions
        'admin_withdraw',
        'get_pool_status'
    ]
    
    for component in flow_components:
        if component not in content:
            print(f"❌ Missing flow component: {component}")
            return False
    
    print("✅ All flow components present")
    
    # Check that buy_policy accepts fee parameter
    buy_policy_match = re.search(r'def buy_policy\([^)]*fee: ARC4UInt64', content)
    if not buy_policy_match:
        print("❌ buy_policy doesn't accept fee parameter")
        return False
    
    print("✅ buy_policy accepts fee parameter")
    
    # Check that oracle_settle returns payout
    if 'return ARC4UInt64(payout)' not in content:
        print("❌ oracle_settle doesn't return payout")
        return False
    
    print("✅ oracle_settle returns payout")
    
    return True

def verify_deployment_readiness():
    """Verify the contract is ready for deployment"""
    print("\n🚀 Verifying Deployment Readiness\n")
    
    # Check if artifacts exist
    artifacts_dir = "projects/App-contracts/smart_contracts/artifacts/insurance"
    
    if not os.path.exists(artifacts_dir):
        print(f"❌ Artifacts directory not found: {artifacts_dir}")
        return False
    
    required_artifacts = [
        "AgriGuardInsurance.arc56.json",
        "agri_guard_insurance_client.py",
        "AgriGuardInsurance.approval.teal",
        "AgriGuardInsurance.clear.teal"
    ]
    
    for artifact in required_artifacts:
        artifact_path = os.path.join(artifacts_dir, artifact)
        if not os.path.exists(artifact_path):
            print(f"❌ Missing artifact: {artifact}")
            return False
    
    print("✅ All deployment artifacts present")
    
    # Check deploy config
    deploy_config_path = "projects/App-contracts/smart_contracts/insurance/deploy_config.py"
    
    if not os.path.exists(deploy_config_path):
        print(f"❌ Deploy config not found: {deploy_config_path}")
        return False
    
    with open(deploy_config_path, 'r') as f:
        deploy_content = f.read()
    
    if 'AgriGuardInsuranceClient' not in deploy_content:
        print("❌ Deploy config doesn't reference correct client")
        return False
    
    print("✅ Deploy config is correct")
    
    return True

def main():
    """Run all verification checks"""
    print("🧪 AgriGuard Insurance Contract Verification\n")
    
    checks = [
        ("Contract Structure", verify_contract_structure),
        ("Contract Flow", verify_contract_flow),
        ("Deployment Readiness", verify_deployment_readiness)
    ]
    
    passed = 0
    total = len(checks)
    
    for check_name, check_func in checks:
        print(f"\n{'='*50}")
        print(f"Checking: {check_name}")
        print('='*50)
        
        if check_func():
            print(f"✅ {check_name} verification passed")
            passed += 1
        else:
            print(f"❌ {check_name} verification failed")
    
    print(f"\n{'='*50}")
    print(f"📊 Verification Results: {passed}/{total} checks passed")
    print('='*50)
    
    if passed == total:
        print("🎉 Contract is ready for deployment and testing!")
        print("\nNext steps:")
        print("1. Start LocalNet: algokit localnet start")
        print("2. Deploy contract: algokit project deploy")
        print("3. Test with Dappflow: algokit explore")
        return True
    else:
        print("⚠️  Some verification checks failed. Please fix the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
