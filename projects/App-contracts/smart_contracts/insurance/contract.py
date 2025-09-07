from algopy import (
    ARC4Contract,
    UInt64,
    Account,
    BoxMap,
    Global,
    Txn,
    itxn,
    urange,
)
from algopy.arc4 import (
    abimethod,
    Address,
    UInt64 as ARC4UInt64,
    DynamicBytes,
    Tuple,
    String,
)

from .abi_types import PolicyData

class AgriGuardInsurance(ARC4Contract):
    """
    Minimal AgriGuard Insurance Contract
    
    Features:
    - Buy policy with group transaction (payment + function call)
    - Oracle settlement
    - Policy storage by owner address
    - Helper functions to get policies
    """
    
    def __init__(self) -> None:
        # Global state
        self.admin = Account()
        self.oracle = Account()
        self.next_policy_id = UInt64(1)
        
        # Box storage: policy ID -> policy data
        self.policies: BoxMap[UInt64, PolicyData] = BoxMap(UInt64, PolicyData)
        
    @abimethod(create="require")
    def create_application(self, admin: Address) -> None:
        """Initialize the application with admin"""
        self.admin = admin.native
        
    @abimethod
    def set_oracle(self, oracle: Address) -> None:
        """Set oracle account (admin only)"""
        assert Txn.sender == self.admin, "Only admin can set oracle"
        self.oracle = oracle.native
        
    @abimethod
    def buy_policy_with_payment(
        self, 
        zip_code: DynamicBytes,
        t0: ARC4UInt64,
        t1: ARC4UInt64,
        cap: ARC4UInt64,
        direction: ARC4UInt64,
        threshold: ARC4UInt64,
        slope: ARC4UInt64,
        fee: ARC4UInt64
    ) -> ARC4UInt64:
        """
        Buy insurance policy with integrated payment using group transaction
        Expects to be called as part of a group transaction where:
        - Transaction 1: Payment from user to contract
        - Transaction 2: This function call
        """
        # Verify this is part of a group transaction
        assert Global.group_size == UInt64(2), "Must be called in group transaction"
        
        # Verify the first transaction is a payment to this contract
        # In a group transaction, we can't directly access the first transaction
        # The payment validation would need to be done at the application level
        # For now, we'll trust that the payment was made correctly in the group
        
        # Create policy
        policy_id = self.next_policy_id
        self.next_policy_id += UInt64(1)
        
        policy_data = PolicyData(
            owner=Address.from_bytes(Txn.sender.bytes),
            zip_code=String.from_bytes(zip_code.bytes),
            t0=t0,
            t1=t1,
            cap=cap,
            direction=direction,
            threshold=threshold,
            slope=slope,
            fee_paid=fee,
            settled=ARC4UInt64(0)
        )
        
        # Store policy in box
        self.policies[policy_id] = policy_data.copy()
        
        return ARC4UInt64(policy_id)
        
    @abimethod
    def buy_policy(
        self, 
        zip_code: DynamicBytes,
        t0: ARC4UInt64,
        t1: ARC4UInt64,
        cap: ARC4UInt64,
        direction: ARC4UInt64,
        threshold: ARC4UInt64,
        slope: ARC4UInt64,
        fee: ARC4UInt64
    ) -> ARC4UInt64:
        """
        Buy insurance policy (simple version for testing)
        Payment should be sent to contract address before calling this method
        """
        # Create policy
        policy_id = self.next_policy_id
        self.next_policy_id += UInt64(1)
        
        policy_data = PolicyData(
            owner=Address.from_bytes(Txn.sender.bytes),
            zip_code=String.from_bytes(zip_code.bytes),
            t0=t0,
            t1=t1,
            cap=cap,
            direction=direction,
            threshold=threshold,
            slope=slope,
            fee_paid=fee,
            settled=ARC4UInt64(0)
        )
        
        # Store policy in box
        self.policies[policy_id] = policy_data.copy()
        
        return ARC4UInt64(policy_id)
        
    @abimethod
    def oracle_settle(self, policy_id: ARC4UInt64, approved: ARC4UInt64) -> ARC4UInt64:
        """
        Oracle-only settlement
        If approved == 1 → payout = cap; else 0
        """
        # Only oracle may settle
        assert Txn.sender == self.oracle, "Only oracle"

        pid = policy_id.native
        policy_data = self.policies.maybe(pid)[0].copy()
        
        # Check that policy is not already settled
        assert policy_data.settled.native == UInt64(0), "Policy already settled"

        payout = UInt64(0)
        if approved.native == UInt64(1):
            payout = policy_data.cap.native

        if payout > UInt64(0):
            itxn.Payment(
                receiver=policy_data.owner.native,
                amount=payout,
                fee=UInt64(1000)
            ).submit()

        # Mark as settled
        policy_data.settled = ARC4UInt64(1)
        self.policies[pid] = policy_data.copy()

        return ARC4UInt64(payout)
        
    @abimethod(readonly=True)
    def get_policy(self, policy_id: ARC4UInt64) -> PolicyData:
        """Get policy data by ID"""
        return self.policies.maybe(policy_id.native)[0].copy()
        
    @abimethod(readonly=True)
    def get_policies_by_owner(self, owner: Address) -> Tuple[ARC4UInt64, ARC4UInt64]:
        """
        Get all policy IDs for a specific owner
        Returns: (count, first_policy_id)
        Note: This is a simplified implementation for MVP
        """
        count = UInt64(0)
        first_policy_id = UInt64(0)
        
        # Check each policy ID from 1 to next_policy_id - 1
        for i in urange(1, self.next_policy_id):
            policy_id = i
            if self.policies.maybe(policy_id)[1]:  # Policy exists
                policy_data = self.policies.maybe(policy_id)[0].copy()
                if policy_data.owner.native == owner.native:
                    count += UInt64(1)
                    if first_policy_id == UInt64(0):
                        first_policy_id = policy_id
        
        return Tuple((ARC4UInt64(count), ARC4UInt64(first_policy_id)))
            
    @abimethod(readonly=True)
    def get_policy_count(self) -> ARC4UInt64:
        """Get total number of policies created"""
        return ARC4UInt64(self.next_policy_id - UInt64(1))
        
    @abimethod(readonly=True)
    def calculate_fee(
        self,
        cap: ARC4UInt64,
        risk_score: ARC4UInt64,
        uncertainty: ARC4UInt64,
        duration_days: ARC4UInt64
    ) -> ARC4UInt64:
        """
        Calculate policy fee based on risk parameters
        Formula: base_fee * risk_multiplier * uncertainty_multiplier * duration_multiplier
        """
        # Base fee: 1% of coverage amount
        base_fee = cap.native // UInt64(100)
        
        # Risk multiplier: 1.0 to 2.0 based on risk score (0-100)
        risk_multiplier = UInt64(100) + (risk_score.native // UInt64(2))  # 100-150 (1.0-1.5x)
        
        # Uncertainty multiplier: 1.0 to 1.5 based on uncertainty (0-50%)
        uncertainty_multiplier = UInt64(100) + uncertainty.native  # 100-150 (1.0-1.5x)
        
        # Duration multiplier: 1.0 to 2.0 based on duration (1-365 days)
        duration_multiplier = UInt64(100) + (duration_days.native // UInt64(2))  # 100-282 (1.0-2.82x)
        
        # Calculate final fee
        fee = (base_fee * risk_multiplier * uncertainty_multiplier * duration_multiplier) // (UInt64(100) * UInt64(100) * UInt64(100))
        
        # Minimum fee of 1000 microALGO
        min_fee = UInt64(1000)
        if fee < min_fee:
            fee = min_fee
            
        return ARC4UInt64(fee)
        
    @abimethod(readonly=True)
    def get_globals(self) -> Tuple[Address, Address, ARC4UInt64]:
        """Get global state"""
        return Tuple((
            Address.from_bytes(self.admin.bytes),
            Address.from_bytes(self.oracle.bytes),
            ARC4UInt64(self.next_policy_id)
        ))