/**
 * Mock Dispute Contract Client for Demo
 * Simulates all dispute contract interactions with realistic responses
 */

import { 
  ALL_MOCK_DISPUTES, 
  MOCK_WALLET_ADDRESS, 
  MOCK_JUROR_DATA,
  MOCK_ASSIGNED_DISPUTES,
  DisputeData,
  JurorData,
  formatAddress,
  getDisputeStatus
} from './mockData';

export interface DisputeClient {
  createDispute(args: { policyId: bigint }): Promise<{ return: bigint }>;
  getDispute(args: { disputeId: bigint }): Promise<{ return: DisputeData }>;
  registerJuror(): Promise<{ return: bigint }>;
  getJurorInfo(args: { jurorAddress: string }): Promise<{ return: JurorData }>;
  voteOnDispute(args: { disputeId: bigint; vote: bigint }): Promise<{ return: bigint }>;
  getDisputesAssignedToJuror(args: { jurorAddress: string }): Promise<{ return: bigint[] }>;
  getDisputeStatus(args: { disputeId: bigint }): Promise<{ return: bigint }>;
  getJurorAssignedDisputes(args: { jurorAddress: string }): Promise<{ return: string }>;
  isJurorAssignedToDispute(args: { jurorAddress: string; disputeId: bigint }): Promise<{ return: bigint }>;
}

export class MockDisputeClient implements DisputeClient {
  private nextDisputeId = 4n; // Start after existing mock disputes
  private userVotes = new Map<string, bigint>(); // Track user votes: "disputeId" -> vote
  
  async createDispute(args: { policyId: bigint }): Promise<{ return: bigint }> {
    await this.delay(1800);
    
    console.log(`⚖️ Creating dispute for policy ${args.policyId}`);
    
    // Create new dispute
    const disputeId = this.nextDisputeId++;
    const newDispute: DisputeData = {
      policy_id: args.policyId,
      claimant: MOCK_WALLET_ADDRESS,
      created_at: BigInt(Date.now()),
      resolved: 0n, // Pending
      yes_votes: 0n,
      no_votes: 0n,
      total_votes: 0n,
      reason: "Claim submitted via AgriGuard interface - awaiting juror review",
      voting_deadline: BigInt(Date.now() + 7 * 24 * 60 * 60 * 1000), // 7 days from now
      resolution_round: BigInt(Date.now() + 10 * 24 * 60 * 60 * 1000) // 10 days from now
    };
    
    // Add to mock storage
    ALL_MOCK_DISPUTES.set(disputeId, newDispute);
    
    console.log(`✅ Dispute created with ID: ${disputeId}, assigned to jurors`);
    return { return: disputeId };
  }
  
  async getDispute(args: { disputeId: bigint }): Promise<{ return: DisputeData }> {
    await this.delay(600);
    
    const dispute = ALL_MOCK_DISPUTES.get(args.disputeId);
    if (!dispute) {
      throw new Error(`Dispute ${args.disputeId} not found`);
    }
    
    console.log(`📋 Retrieved dispute ${args.disputeId} - Status: ${getDisputeStatus(dispute)}`);
    return { return: dispute };
  }
  
  async registerJuror(): Promise<{ return: bigint }> {
    await this.delay(2200);
    
    console.log(`👨‍⚖️ Registering ${formatAddress(MOCK_WALLET_ADDRESS)} as juror`);
    console.log(`💰 Staking 1000 ALGO for juror registration`);
    
    // Simulate successful registration
    const registrationId = BigInt(Date.now());
    
    console.log(`✅ Juror registered successfully with ID: ${registrationId}`);
    return { return: registrationId };
  }
  
  async getJurorInfo(args: { jurorAddress: string }): Promise<{ return: JurorData }> {
    await this.delay(500);
    
    // For demo, return mock data for current user, null for others
    if (args.jurorAddress === MOCK_WALLET_ADDRESS) {
      console.log(`👨‍⚖️ Retrieved juror info - Reputation: ${MOCK_JUROR_DATA.reputation}%, Total votes: ${MOCK_JUROR_DATA.total_votes}`);
      return { return: MOCK_JUROR_DATA };
    } else {
      // For other addresses, simulate unregistered juror
      throw new Error("Juror not registered");
    }
  }
  
  async voteOnDispute(args: { disputeId: bigint; vote: bigint }): Promise<{ return: bigint }> {
    await this.delay(1600);
    
    const dispute = ALL_MOCK_DISPUTES.get(args.disputeId);
    if (!dispute) {
      throw new Error(`Dispute ${args.disputeId} not found`);
    }
    
    const voteKey = `${args.disputeId}`;
    const voteText = args.vote === 1n ? "YES (Approve)" : "NO (Reject)";
    
    console.log(`🗳️ Voting ${voteText} on dispute ${args.disputeId}`);
    
    // Update vote counts
    const updatedDispute = { ...dispute };
    if (args.vote === 1n) {
      updatedDispute.yes_votes += 1n;
    } else {
      updatedDispute.no_votes += 1n;
    }
    updatedDispute.total_votes += 1n;
    
    // Store the vote
    this.userVotes.set(voteKey, args.vote);
    ALL_MOCK_DISPUTES.set(args.disputeId, updatedDispute);
    
    console.log(`✅ Vote recorded - Current tally: YES: ${updatedDispute.yes_votes}, NO: ${updatedDispute.no_votes}`);
    
    return { return: 1n }; // Success
  }
  
  async getDisputesAssignedToJuror(args: { jurorAddress: string }): Promise<{ return: bigint[] }> {
    await this.delay(700);
    
    if (args.jurorAddress === MOCK_WALLET_ADDRESS) {
      console.log(`📋 Retrieved ${MOCK_ASSIGNED_DISPUTES.length} disputes assigned for voting`);
      return { return: MOCK_ASSIGNED_DISPUTES };
    } else {
      return { return: [] };
    }
  }
  
  async getDisputeStatus(args: { disputeId: bigint }): Promise<{ return: bigint }> {
    await this.delay(400);
    
    const dispute = ALL_MOCK_DISPUTES.get(args.disputeId);
    if (!dispute) {
      throw new Error(`Dispute ${args.disputeId} not found`);
    }
    
    console.log(`📊 Dispute ${args.disputeId} status: ${dispute.resolved}`);
    return { return: dispute.resolved };
  }
  
  async getJurorAssignedDisputes(args: { jurorAddress: string }): Promise<{ return: string }> {
    await this.delay(600);
    
    if (args.jurorAddress === MOCK_WALLET_ADDRESS) {
      const disputeList = MOCK_ASSIGNED_DISPUTES.join(',');
      console.log(`📋 Assigned disputes string: ${disputeList}`);
      return { return: disputeList };
    } else {
      return { return: "" };
    }
  }
  
  async isJurorAssignedToDispute(args: { jurorAddress: string; disputeId: bigint }): Promise<{ return: bigint }> {
    await this.delay(350);
    
    if (args.jurorAddress === MOCK_WALLET_ADDRESS) {
      const isAssigned = MOCK_ASSIGNED_DISPUTES.includes(args.disputeId) ? 1n : 0n;
      console.log(`🔍 Juror ${isAssigned === 1n ? 'IS' : 'IS NOT'} assigned to dispute ${args.disputeId}`);
      return { return: isAssigned };
    } else {
      return { return: 0n };
    }
  }
  
  // Helper method to check if user has voted on a dispute
  hasUserVoted(disputeId: bigint): boolean {
    return this.userVotes.has(`${disputeId}`);
  }
  
  // Helper method to get user's vote on a dispute
  getUserVote(disputeId: bigint): bigint | undefined {
    return this.userVotes.get(`${disputeId}`);
  }
  
  private async delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}

// Export singleton instance
export const mockDisputeClient = new MockDisputeClient();
