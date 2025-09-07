#!/usr/bin/env python3
"""
Test runner for AgriGuard Insurance Contract
"""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def run_tests():
    """Run all contract tests"""
    try:
        import pytest
        
        # Run the tests
        result = pytest.main([
            "test_insurance_contract.py",
            "-v",
            "--tb=short",
            "--color=yes"
        ])
        
        if result == 0:
            print("\n✅ All tests passed!")
        else:
            print("\n❌ Some tests failed!")
            
        return result
        
    except ImportError as e:
        print(f"❌ Missing dependencies: {e}")
        print("Please install test dependencies:")
        print("pip install -r requirements-test.txt")
        return 1

if __name__ == "__main__":
    exit_code = run_tests()
    sys.exit(exit_code)
