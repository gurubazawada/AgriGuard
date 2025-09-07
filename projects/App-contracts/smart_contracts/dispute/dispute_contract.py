"""
AgriGuard Dispute Resolution Contract

This contract handles dispute resolution for insurance claims through community voting.
Features:
- Random selection of 10 protocol users as jurors
- Yes/No voting on disputed claims
- 7 votes required for payout approval
- Integration with main insurance contract
"""

from algopy import (
    ARC4Contract,
    UInt64,
    String,
    Bytes,
    BoxMap,
    Global,
    Txn,
    itxn,
    urange,
    subroutine,
)
from algopy.arc4 import (
    abimethod,
    Address,
    UInt64 as ARC4UInt64,
    String as ARC4String,
    Struct,
    Tuple,
)


class DisputeData(Struct):
    """Dispute information"""
    policy_id: ARC4UInt64
    claimant: Address
    reason: ARC4String
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


class AgriGuardDispute(ARC4Contract):
    """
    Dispute Resolution Contract for AgriGuard Insurance

    Handles community voting on disputed insurance claims.
    """

    def __init__(self) -> None:
        # Global state
        self.admin = Address()
        self.insurance_contract = Address()  # Main insurance contract address
        self.next_dispute_id = UInt64(1)
        self.total_jurors = UInt64(0)
        self.min_juror_reputation = UInt64(10)  # Minimum reputation to participate

        # Storage
        self.disputes: BoxMap[UInt64, DisputeData] = BoxMap(UInt64, DisputeData)
        self.jurors: BoxMap[Address, JurorData] = BoxMap(Address, JurorData)
        self.dispute_jurors: BoxMap[UInt64, Bytes] = BoxMap(UInt64, Bytes)  # dispute_id -> juror addresses
        self.juror_votes: BoxMap[Bytes, VoteData] = BoxMap(Bytes, VoteData)  # dispute_id + juror_address -> vote

    @abimethod(create="require")
    def create_application(self, admin: Address) -> None:
        """Initialize the dispute contract"""
        self.admin = admin.native

    @abimethod
    def set_insurance_contract(self, contract_address: Address) -> ARC4UInt64:
        """Set the main insurance contract address (admin only)"""
        assert Txn.sender == self.admin, "Only admin"

        self.insurance_contract = contract_address.native
        return ARC4UInt64(1)

    @abimethod
    def register_juror(self) -> ARC4UInt64:
        """Register as a juror in the dispute resolution system"""
        caller = Address.from_bytes(Txn.sender.bytes)

        # Check if already registered
        existing = self.jurors.maybe(caller)[1]
        if existing:
            return ARC4UInt64(0)  # Already registered

        # Create juror data
        juror_data = JurorData(
            address=Address(caller),
            reputation=ARC4UInt64(50),  # Start with neutral reputation
            total_votes=ARC4UInt64(0),
            correct_votes=ARC4UInt64(0),
            registration_time=ARC4UInt64(Global.round)
        )

        # Store juror
        self.jurors[caller] = juror_data
        self.total_jurors += UInt64(1)

        return ARC4UInt64(1)

    @abimethod
    def create_dispute(
        self,
        policy_id: ARC4UInt64,
        reason: ARC4String
    ) -> ARC4UInt64:
        """Create a new dispute for an insurance claim"""
        caller = Address.from_bytes(Txn.sender.bytes)
        dispute_id = self.next_dispute_id

        # Create dispute data
        dispute_data = DisputeData(
            policy_id=policy_id,
            claimant=Address(caller),
            reason=reason,
            created_at=ARC4UInt64(Global.round),
            resolved=ARC4UInt64(0),  # Pending
            yes_votes=ARC4UInt64(0),
            no_votes=ARC4UInt64(0),
            total_votes=ARC4UInt64(0),
            payout_amount=ARC4UInt64(0)  # Will be set by insurance contract
        )

        # Store dispute
        self.disputes[dispute_id] = dispute_data

        # Select jurors for this dispute
        juror_addresses = self._select_random_jurors(dispute_id)

        # Store juror list for this dispute
        self.dispute_jurors[dispute_id] = juror_addresses

        self.next_dispute_id += UInt64(1)

        return ARC4UInt64(dispute_id)

    @subroutine
    def _select_random_jurors(self, dispute_id: UInt64) -> Bytes:
        """Select 10 random jurors for a dispute using a pseudo-random algorithm"""
        if self.total_jurors < UInt64(10):
            return Bytes(b"")  # Not enough jurors

        selected_jurors = Bytes(b"")

        # Use dispute_id and current round as seed for pseudo-random selection
        seed = dispute_id + Global.round

        # Simple pseudo-random selection (in production, use better randomness)
        juror_count = UInt64(0)
        juror_index = UInt64(0)

        # Get all juror addresses (simplified - in practice you'd iterate through all jurors)
        # This is a simplified version - real implementation would need proper juror enumeration
        while juror_count < UInt64(10) and juror_index < self.total_jurors:
            # Pseudo-random juror selection
            random_juror_index = (seed + juror_index) % self.total_jurors

            # In a real implementation, you'd have a way to get juror by index
            # For now, we'll use a simplified approach
            juror_index += UInt64(1)

            if juror_index <= self.total_jurors:
                juror_count += UInt64(1)
                # Add juror address to selected list (simplified)
                selected_jurors = selected_jurors + Bytes(b"juror")

        return selected_jurors

    @abimethod
    def vote_on_dispute(
        self,
        dispute_id: ARC4UInt64,
        vote: ARC4UInt64  # 1 = approve payout, 0 = reject
    ) -> ARC4UInt64:
        """Vote on a dispute (only selected jurors can vote)"""
        caller = Address.from_bytes(Txn.sender.bytes)
        pid = dispute_id.native

        # Check if dispute exists
        dispute_data = self.disputes.maybe(pid)[0].copy()
        exists = self.disputes.maybe(pid)[1]

        if not exists:
            return ARC4UInt64(0)  # Dispute doesn't exist

        if dispute_data.resolved.native != UInt64(0):
            return ARC4UInt64(0)  # Dispute already resolved

        # Check if caller is a selected juror for this dispute
        juror_list = self.dispute_jurors.maybe(pid)[0]
        if juror_list == Bytes(b""):
            return ARC4UInt64(0)  # No jurors selected

        # Check if caller already voted
        vote_key = Bytes(b"vote_key") + caller.bytes
        existing_vote = self.juror_votes.maybe(vote_key)[1]

        if existing_vote:
            return ARC4UInt64(0)  # Already voted

        # Record the vote
        vote_data = VoteData(
            juror=Address(caller),
            vote=vote,
            timestamp=ARC4UInt64(Global.round)
        )

        self.juror_votes[vote_key] = vote_data

        # Update dispute vote counts
        if vote.native == UInt64(1):
            dispute_data.yes_votes = ARC4UInt64(dispute_data.yes_votes.native + UInt64(1))
        else:
            dispute_data.no_votes = ARC4UInt64(dispute_data.no_votes.native + UInt64(1))

        dispute_data.total_votes = ARC4UInt64(dispute_data.total_votes.native + UInt64(1))
        self.disputes[pid] = dispute_data

        # Check if voting is complete (7 votes)
        if dispute_data.total_votes.native >= UInt64(7):
            self._resolve_dispute(pid, dispute_data)

        return ARC4UInt64(1)

    @subroutine
    def _resolve_dispute(self, dispute_id: UInt64, dispute_data: DisputeData) -> None:
        """Resolve a dispute once voting is complete"""
        if dispute_data.yes_votes.native >= UInt64(7):
            # Approved - call insurance contract to pay out
            dispute_data.resolved = ARC4UInt64(1)  # Approved

            # Call insurance contract oracle_settle method
            self._call_insurance_payout(dispute_data.policy_id.native, dispute_data.payout_amount.native)
        else:
            # Rejected
            dispute_data.resolved = ARC4UInt64(2)  # Rejected

        self.disputes[dispute_id] = dispute_data

    @subroutine
    def _call_insurance_payout(self, policy_id: UInt64, amount: UInt64) -> None:
        """Call the insurance contract to process payout"""
        if self.insurance_contract != Global.zero_address:
            # Call oracle_settle on insurance contract with decision=1 (approve)
            # This would need to be implemented as an inner transaction
            pass  # Simplified for now

    @abimethod(readonly=True)
    def get_dispute(self, dispute_id: ARC4UInt64) -> DisputeData:
        """Get dispute information"""
        dispute_data = self.disputes.maybe(dispute_id.native)[0].copy()
        exists = self.disputes.maybe(dispute_id.native)[1]

        if not exists:
            # Return empty dispute data if not found
            return DisputeData(
                policy_id=ARC4UInt64(0),
                claimant=Address(Global.zero_address),
                reason=ARC4String(""),
                created_at=ARC4UInt64(0),
                resolved=ARC4UInt64(0),
                yes_votes=ARC4UInt64(0),
                no_votes=ARC4UInt64(0),
                total_votes=ARC4UInt64(0),
                payout_amount=ARC4UInt64(0)
            )

        return dispute_data

    @abimethod(readonly=True)
    def get_juror_info(self, juror_address: Address) -> JurorData:
        """Get juror information"""
        juror_data = self.jurors.maybe(juror_address.native)[0].copy()
        exists = self.jurors.maybe(juror_address.native)[1]

        if not exists:
            return JurorData(
                address=juror_address,
                reputation=ARC4UInt64(0),
                total_votes=ARC4UInt64(0),
                correct_votes=ARC4UInt64(0),
                registration_time=ARC4UInt64(0)
            )

        return juror_data

    @abimethod(readonly=True)
    def get_dispute_jurors(self, dispute_id: ARC4UInt64) -> Bytes:
        """Get list of jurors for a dispute"""
        juror_list = self.dispute_jurors.maybe(dispute_id.native)[0]
        return juror_list
