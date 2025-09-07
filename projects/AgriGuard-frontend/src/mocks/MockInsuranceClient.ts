/**
 * Mock Insurance Contract Client for Demo
 * Simulates all insurance contract interactions with realistic responses
 */

import { 
  MOCK_POLICIES, 
  MOCK_WALLET_ADDRESS, 
  PolicyData,
  formatAlgo 
} from './mockData';

export interface InsuranceClient {
  buyPolicy(args: {
    zipCode: string;
    t0: bigint;
    t1: bigint;
    cap: bigint;
    direction: bigint;
    threshold: bigint;
    slope: bigint;
    fee: bigint;
  }): Promise<{ return: bigint }>;
  
  getPolicy(args: { policyId: bigint }): Promise<{ return: PolicyData }>;
  getPoliciesByOwner(args: { owner: string }): Promise<{ return: [bigint, bigint] }>;
  getPolicyCount(): Promise<{ return: bigint }>;
  calculateFee(args: {
    cap: bigint;
    riskScore: bigint;
    uncertainty: bigint;
    durationDays: bigint;
  }): Promise<{ return: bigint }>;
  getGlobals(): Promise<{ return: [string, string, bigint] }>;
  oracleSettle(args: { policyId: bigint; approved: bigint }): Promise<{ return: bigint }>;
}

export class MockInsuranceClient implements InsuranceClient {
  private nextPolicyId = 4n; // Start after existing mock policies
  
  async buyPolicy(args: {
    zipCode: string;
    t0: bigint;
    t1: bigint;
    cap: bigint;
    direction: bigint;
    threshold: bigint;
    slope: bigint;
    fee: bigint;
  }): Promise<{ return: bigint }> {
    // Simulate network delay
    await this.delay(1500);
    
    console.log(`🏗️ Buying policy for ZIP ${args.zipCode}, Coverage: ${formatAlgo(args.cap)} ALGO`);
    
    // Create new policy
    const policyId = this.nextPolicyId++;
    const newPolicy: PolicyData = {
      owner: MOCK_WALLET_ADDRESS,
      zipCode: args.zipCode,
      t0: args.t0,
      t1: args.t1,
      cap: args.cap,
      direction: args.direction,
      threshold: args.threshold,
      slope: args.slope,
      feePaid: args.fee,
      settled: 0n
    };
    
    // Add to mock storage
    MOCK_POLICIES.set(policyId, newPolicy);
    
    console.log(`✅ Policy created with ID: ${policyId}`);
    
    return { return: policyId };
  }
  
  async getPolicy(args: { policyId: bigint }): Promise<{ return: PolicyData }> {
    await this.delay(500);
    
    const policy = MOCK_POLICIES.get(args.policyId);
    if (!policy) {
      throw new Error(`Policy ${args.policyId} not found`);
    }
    
    console.log(`📋 Retrieved policy ${args.policyId} for ZIP ${policy.zipCode}`);
    return { return: policy };
  }
  
  async getPoliciesByOwner(args: { owner: string }): Promise<{ return: [bigint, bigint] }> {
    await this.delay(800);
    
    const userPolicies = Array.from(MOCK_POLICIES.entries())
      .filter(([_, policy]) => policy.owner === args.owner);
    
    const count = BigInt(userPolicies.length);
    const firstPolicyId = userPolicies.length > 0 ? userPolicies[0][0] : 0n;
    
    console.log(`👤 User has ${count} policies, first policy ID: ${firstPolicyId}`);
    return { return: [count, firstPolicyId] };
  }
  
  async getPolicyCount(): Promise<{ return: bigint }> {
    await this.delay(300);
    
    const count = BigInt(MOCK_POLICIES.size);
    console.log(`📊 Total policies in system: ${count}`);
    return { return: count };
  }
  
  async calculateFee(args: {
    cap: bigint;
    riskScore: bigint;
    uncertainty: bigint;
    durationDays: bigint;
  }): Promise<{ return: bigint }> {
    await this.delay(600);
    
    // Simulate realistic fee calculation
    const baseFee = args.cap / 100n; // 1% of coverage
    const riskMultiplier = 100n + (args.riskScore / 2n); // 100-150 (1.0-1.5x)
    const uncertaintyMultiplier = 100n + args.uncertainty; // 100-150 (1.0-1.5x)
    const durationMultiplier = 100n + (args.durationDays / 2n); // 100-282 (1.0-2.82x)
    
    let fee = (baseFee * riskMultiplier * uncertaintyMultiplier * durationMultiplier) / 1000000n;
    
    // Minimum fee of 1000 microALGO
    const minFee = 1000n;
    if (fee < minFee) {
      fee = minFee;
    }
    
    console.log(`💰 Calculated fee: ${formatAlgo(fee)} ALGO for ${formatAlgo(args.cap)} ALGO coverage`);
    return { return: fee };
  }
  
  async getGlobals(): Promise<{ return: [string, string, bigint] }> {
    await this.delay(400);
    
    const admin = "ADMIN7MOCK4TESTINGPURPOSES9ABCDEFGHIJKLMNOP";
    const oracle = "ORACLE7MOCK4TESTINGPURPOSES9ABCDEFGHIJKLMNO";
    const nextPolicyId = this.nextPolicyId;
    
    console.log(`🌐 Global state - Admin: ${admin.slice(0, 8)}..., Oracle: ${oracle.slice(0, 8)}..., Next ID: ${nextPolicyId}`);
    return { return: [admin, oracle, nextPolicyId] };
  }
  
  async oracleSettle(args: { policyId: bigint; approved: bigint }): Promise<{ return: bigint }> {
    await this.delay(2000);
    
    const policy = MOCK_POLICIES.get(args.policyId);
    if (!policy) {
      throw new Error(`Policy ${args.policyId} not found`);
    }
    
    const payout = args.approved === 1n ? policy.cap : 0n;
    
    // Update policy as settled
    const updatedPolicy = { ...policy, settled: 1n };
    MOCK_POLICIES.set(args.policyId, updatedPolicy);
    
    console.log(`🏛️ Oracle settlement - Policy ${args.policyId}, Approved: ${args.approved === 1n}, Payout: ${formatAlgo(payout)} ALGO`);
    return { return: payout };
  }
  
  private async delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}

// Export singleton instance
export const mockInsuranceClient = new MockInsuranceClient();
