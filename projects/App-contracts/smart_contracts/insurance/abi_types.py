"""
Minimal ABI Type definitions for AgriGuard Insurance
"""

from algopy.arc4 import (
    Address,
    UInt64 as ARC4UInt64,
    String,
    Struct,
)


class PolicyData(Struct):
    """Minimal policy data structure"""
    owner: Address
    zip_code: String  
    t0: ARC4UInt64  # start time (unix seconds)
    t1: ARC4UInt64  # end time (unix seconds)
    cap: ARC4UInt64  # payout amount in microALGOs
    direction: ARC4UInt64  # 1 => trigger when < threshold; 0 => trigger when > threshold
    threshold: ARC4UInt64  # threshold value
    slope: ARC4UInt64  # slope calculation
    fee_paid: ARC4UInt64  # fee paid for policy
    settled: ARC4UInt64  # 0 = not settled, 1 = settled