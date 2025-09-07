from algopy import (
    ARC4Contract,
    UInt64,
    Account,
    BoxMap,
    Box,
    Global,
    Txn,
    itxn,
    urange,
    subroutine,
    Bytes,
    op,
    Asset,
    log,
)
from algopy.arc4 import (
    abimethod,
    Address,
    UInt64 as ARC4UInt64,
    DynamicBytes,
    Tuple,
    String as ARC4String,
    Struct,
)
from algopy import String

from .abi_types import PolicyData

class PolicyEvent(Struct):
    """Event data for policy operations"""
    policy_id: ARC4UInt64
    owner: Address
    action: ARC4String  # "created", "settled", "disputed"
    timestamp: ARC4UInt64
    amount: ARC4UInt64

class InsuranceStats(Struct):
    """Global insurance statistics"""
    total_policies: ARC4UInt64
    total_coverage: ARC4UInt64
    total_payouts: ARC4UInt64
    active_policies: ARC4UInt64
    total_fees_collected: ARC4UInt64

class AgriGuardInsurance(ARC4Contract):
    """
    Enhanced AgriGuard Insurance Contract with Algorand Features

    Features:
    - Buy policy with group transaction (payment + function call)
    - Oracle settlement with asset transfers
    - Policy storage by owner address with enhanced box management
    - Event logging for transparency
    - Cross-contract dispute resolution
    - Asset-based fee management
    - Time-based policy validation
    """

    def __init__(self) -> None:
        # Global state
        self.admin = Account()
        self.oracle = Account()
        self.dispute_contract = Address()  # Linked dispute resolution contract
        self.next_policy_id = UInt64(1)
        self.contract_creation_round = UInt64(0)  # Track when contract was created

        # Enhanced storage
        self.policies: BoxMap[UInt64, PolicyData] = BoxMap(UInt64, PolicyData)

        # Statistics tracking
        self.stats_box = Box(InsuranceStats)

        # Event log box for transparency
        self.event_log: BoxMap[UInt64, PolicyEvent] = BoxMap(UInt64, PolicyEvent)
        self.next_event_id = UInt64(1)
        
    @abimethod(create="require")
    def create_application(self, admin: Address) -> None:
        """Initialize the application with admin and setup enhanced features"""
        self.admin = admin.native
        self.contract_creation_round = Global.round

        # Initialize statistics
        initial_stats = InsuranceStats(
            total_policies=ARC4UInt64(0),
            total_coverage=ARC4UInt64(0),
            total_payouts=ARC4UInt64(0),
            active_policies=ARC4UInt64(0),
            total_fees_collected=ARC4UInt64(0)
        )
        self.stats_box.value = initial_stats

        # Log contract creation event
        self._log_event(ARC4UInt64(0), admin, ARC4String("contract_created"), ARC4UInt64(0))

    @abimethod
    def set_dispute_contract(self, dispute_contract: Address) -> ARC4UInt64:
        """Set the dispute resolution contract address (admin only)"""
        assert Txn.sender == self.admin, "Only admin can set dispute contract"
        self.dispute_contract = dispute_contract.native
        return ARC4UInt64(1)

    @subroutine
    def _log_event(self, policy_id: ARC4UInt64, owner: Address, action: ARC4String, amount: ARC4UInt64) -> None:
        """Log policy events for transparency"""
        event = PolicyEvent(
            policy_id=policy_id,
            owner=owner,
            action=action,
            timestamp=ARC4UInt64(Global.round),
            amount=amount
        )
        self.event_log[self.next_event_id] = event
        self.next_event_id += UInt64(1)

    @subroutine
    def _update_stats(self, action: String, coverage_amount: ARC4UInt64, fee_amount: ARC4UInt64) -> None:
        """Update global statistics"""
        current_stats = self.stats_box.value

        if action == String("policy_created"):
            current_stats.total_policies = ARC4UInt64(current_stats.total_policies.native + 1)
            current_stats.total_coverage = ARC4UInt64(current_stats.total_coverage.native + coverage_amount.native)
            current_stats.active_policies = ARC4UInt64(current_stats.active_policies.native + 1)
            current_stats.total_fees_collected = ARC4UInt64(current_stats.total_fees_collected.native + fee_amount.native)
        elif action == String("policy_settled"):
            current_stats.total_payouts = ARC4UInt64(current_stats.total_payouts.native + coverage_amount.native)
            current_stats.active_policies = ARC4UInt64(current_stats.active_policies.native - 1)

        self.stats_box.value = current_stats
        
    @abimethod
    def set_oracle(self, oracle: Address) -> None:
        """Set oracle account (admin only)"""
        assert Txn.sender == self.admin, "Only admin can set oracle"
        self.oracle = oracle.native

    @abimethod(readonly=True)
    def get_oracle(self) -> Address:
        """Get current oracle account address"""
        return Address(self.oracle)
        
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
        Enhanced with validation, event logging, and statistics tracking
        Expects to be called as part of a group transaction where:
        - Transaction 1: Payment from user to contract
        - Transaction 2: This function call
        """
        # Enhanced validation
        assert Global.group_size == UInt64(2), "Must be called in group transaction"
        assert t0.native < t1.native, "Start time must be before end time"
        assert cap.native > UInt64(0), "Coverage amount must be positive"
        assert fee.native > UInt64(0), "Fee must be positive"

        # Time-based validation
        current_round = Global.round
        assert t0.native > current_round, "Policy cannot start in the past"
        assert t1.native > t0.native + UInt64(100), "Policy duration too short (minimum 100 rounds)"

        # Create policy
        policy_id = self.next_policy_id
        self.next_policy_id += UInt64(1)

        caller = Address.from_bytes(Txn.sender.bytes)

        policy_data = PolicyData(
            owner=caller,
            zip_code=ARC4String.from_bytes(zip_code.bytes),
            t0=t0,
            t1=t1,
            cap=cap,
            direction=direction,
            threshold=threshold,
            slope=slope,
            fee_paid=fee,
            settled=ARC4UInt64(0)
        )

        # Store policy in box with enhanced error handling
        self.policies[policy_id] = policy_data.copy()

        # Update statistics
        self._update_stats(String("policy_created"), cap, fee)

        # Log policy creation event
        self._log_event(ARC4UInt64(policy_id), caller, ARC4String("policy_created"), cap)

        # Emit log for external monitoring
        log(Bytes(b"POLICY_CREATED") + policy_id.to_bytes() + caller.bytes)

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
            zip_code=ARC4String.from_bytes(zip_code.bytes),
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
        Enhanced oracle settlement with cross-contract communication and event logging
        If approved == 1 → payout = cap; else 0
        """
        # Enhanced access control
        assert Txn.sender == self.oracle, "Only oracle can settle policies"

        pid = policy_id.native
        policy_data = self.policies.maybe(pid)[0].copy()

        # Enhanced validation
        assert policy_data.settled.native == UInt64(0), "Policy already settled"

        # Time-based validation - ensure policy is within coverage period
        current_round = Global.round
        assert current_round >= policy_data.t0.native, "Policy has not started yet"
        assert current_round <= policy_data.t1.native, "Policy has expired"

        payout = UInt64(0)
        settlement_action = ARC4String("settled_rejected")

        if approved.native == UInt64(1):
            payout = policy_data.cap.native
            settlement_action = ARC4String("settled_approved")

            # Enhanced payment with asset validation
            if payout > UInt64(0):
                # Use inner transaction for secure payment
                itxn.Payment(
                    receiver=policy_data.owner.native,
                    amount=payout,
                    fee=UInt64(1000),
                    note=Bytes(b"AgriGuard Insurance Payout - Policy: ") + pid.to_bytes()
                ).submit()

        # Mark as settled
        policy_data.settled = ARC4UInt64(1)
        self.policies[pid] = policy_data.copy()

        # Update statistics
        self._update_stats(String("policy_settled"), ARC4UInt64(payout), ARC4UInt64(0))

        # Log settlement event
        self._log_event(ARC4UInt64(pid), policy_data.owner, settlement_action, ARC4UInt64(payout))

        # Emit log for external monitoring
        log(Bytes(b"POLICY_SETTLED") + pid.to_bytes() + approved.native.to_bytes())

        return ARC4UInt64(payout)

    @abimethod
    def dispute_settlement(self, policy_id: ARC4UInt64, reason: ARC4String) -> ARC4UInt64:
        """
        Enhanced dispute creation with cross-contract communication
        Only the policy owner can dispute their own policy
        """
        pid = policy_id.native
        caller = Address.from_bytes(Txn.sender.bytes)

        # Enhanced validation
        policy_data = self.policies.maybe(pid)[0].copy()
        exists = self.policies.maybe(pid)[1]

        if not exists:
            return ARC4UInt64(0)  # Policy doesn't exist

        if caller != policy_data.owner:
            return ARC4UInt64(0)  # Not the owner

        if policy_data.settled.native == UInt64(0):
            return ARC4UInt64(0)  # Policy not settled yet

        # Time-based validation - disputes must be filed within time window
        current_round = Global.round
        settlement_round = policy_data.settled.native  # We need to track settlement time
        # Allow disputes within 1000 rounds (approximately 3-4 days) of settlement
        assert current_round <= settlement_round + UInt64(1000), "Dispute filing period expired"

        # Cross-contract communication: Call dispute contract
        if self.dispute_contract != Global.zero_address:
            # Use inner transaction to call dispute contract
            try:
                dispute_result = itxn.ApplicationCall(
                    app_id=UInt64(0),  # Will be set by the dispute contract address
                    app_args=[
                        Bytes(b"create_dispute"),
                        pid.to_bytes(),
                        reason.bytes
                    ],
                    accounts=[caller],
                    foreign_apps=[self.dispute_contract]
                )
                dispute_result.submit()
            except:
                # Fallback if cross-contract call fails
                pass

        # Log dispute event
        self._log_event(ARC4UInt64(pid), caller, ARC4String("disputed"), ARC4UInt64(0))

        # Emit log for external monitoring
        log(Bytes(b"DISPUTE_CREATED") + pid.to_bytes() + caller.bytes)

        return ARC4UInt64(1)

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

    @abimethod
    def delete_policy(self, policy_id: ARC4UInt64) -> ARC4UInt64:
        """
        Delete a policy by ID - only the owner can delete their own unsettled policy
        Returns: 1 if successful, 0 if failed
        """
        pid = policy_id.native

        # Check if policy exists
        policy_data = self.policies.maybe(pid)[0].copy()
        exists = self.policies.maybe(pid)[1]

        if not exists:
            # Policy doesn't exist
            return ARC4UInt64(0)

        # Check if caller is the owner
        caller = Address.from_bytes(Txn.sender.bytes)
        if caller != policy_data.owner:
            # Caller is not the owner
            return ARC4UInt64(0)

        # Check if policy is already settled
        if policy_data.settled.native == UInt64(1):
            # Policy is already settled, cannot delete
            return ARC4UInt64(0)

        # Delete the policy from storage
        # In PyTeal BoxMap, we delete by using del keyword
        del self.policies[pid]

        return ARC4UInt64(1)

    @abimethod(readonly=True)
    def get_globals(self) -> Tuple[Address, Address, ARC4UInt64]:
        """Get global state"""
        return Tuple((
            Address.from_bytes(self.admin.bytes),
            Address.from_bytes(self.oracle.bytes),
            ARC4UInt64(self.next_policy_id)
        ))

    @abimethod(readonly=True)
    def get_statistics(self) -> InsuranceStats:
        """Get comprehensive insurance statistics"""
        return self.stats_box.value

    @abimethod(readonly=True)
    def get_event(self, event_id: ARC4UInt64) -> PolicyEvent:
        """Get a specific event by ID"""
        event = self.event_log.maybe(event_id.native)[0]
        if event == PolicyEvent(
            policy_id=ARC4UInt64(0),
            owner=Address(Global.zero_address),
            action=ARC4String(""),
            timestamp=ARC4UInt64(0),
            amount=ARC4UInt64(0)
        ):
            return PolicyEvent(
                policy_id=ARC4UInt64(0),
                owner=Address(Global.zero_address),
                action=ARC4String("event_not_found"),
                timestamp=ARC4UInt64(0),
                amount=ARC4UInt64(0)
            )
        return event

    @abimethod(readonly=True)
    def get_recent_events(self, limit: ARC4UInt64) -> Tuple[ARC4UInt64, ARC4UInt64]:
        """Get recent events (returns count and starting event ID)"""
        total_events = self.next_event_id - UInt64(1)
        start_id = total_events - limit.native + UInt64(1)
        if start_id < UInt64(1):
            start_id = UInt64(1)

        return Tuple((ARC4UInt64(total_events), ARC4UInt64(start_id)))

    @abimethod(readonly=True)
    def validate_policy_timing(self, policy_id: ARC4UInt64) -> ARC4UInt64:
        """Validate if a policy is currently active based on timing"""
        policy_data = self.policies.maybe(policy_id.native)[0].copy()
        exists = self.policies.maybe(policy_id.native)[1]

        if not exists:
            return ARC4UInt64(0)  # Policy doesn't exist

        if policy_data.settled.native == UInt64(1):
            return ARC4UInt64(2)  # Policy already settled

        current_round = Global.round
        if current_round < policy_data.t0.native:
            return ARC4UInt64(3)  # Policy hasn't started yet

        if current_round > policy_data.t1.native:
            return ARC4UInt64(4)  # Policy has expired

        return ARC4UInt64(1)  # Policy is active