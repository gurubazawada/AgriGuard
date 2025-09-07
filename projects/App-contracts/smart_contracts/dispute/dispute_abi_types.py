"""
ABI Type definitions for AgriGuard Dispute Resolution Contract
"""

from algopy.arc4 import (
    Address,
    UInt64 as ARC4UInt64,
    String,
    Struct,
)


class DisputeData(Struct):
    """Dispute information"""
    policy_id: ARC4UInt64
    claimant: Address
    reason: String
    created_at: ARC4UInt64
    resolved: ARC4UInt64  # 0 = pending, 1 = approved, 2 = rejected
    yes_votes: ARC4UInt64
    no_votes: ARC4UInt64
    total_votes: ARC4UInt64
    payout_amount: ARC4UInt64


class VoteData(Struct):
    """Individual vote data"""
    juror: Address
    vote: ARC4UInt64  # 1 = yes, 0 = no
    timestamp: ARC4UInt64


class JurorData(Struct):
    """Juror registration data"""
    address: Address
    reputation: ARC4UInt64  # 0-100, affects selection probability
    total_votes: ARC4UInt64
    correct_votes: ARC4UInt64
    registration_time: ARC4UInt64
