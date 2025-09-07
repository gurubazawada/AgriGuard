/**
 * Mock data for AgriGuard demo
 * Simulates a working application with realistic policy and dispute data
 */

export interface PolicyData {
  owner: string
  zipCode: string
  t0: bigint
  t1: bigint
  cap: bigint
  direction: bigint
  threshold: bigint
  slope: bigint
  feePaid: bigint
  settled: bigint
}

export interface DisputeData {
  policy_id: bigint
  claimant: string
  created_at: bigint
  resolved: bigint  // 0 = pending/active, 1 = approved, 2 = rejected
  yes_votes: bigint
  no_votes: bigint
  total_votes: bigint
  reason: string
  voting_deadline: bigint
  resolution_round: bigint
}

export interface JurorData {
  address: string
  reputation: bigint
  total_votes: bigint
  correct_votes: bigint
  registration_round: bigint
  last_vote_round: bigint
  staked_amount: bigint
}

// Mock connected wallet address
export const MOCK_WALLET_ADDRESS = "DEMO7MOCKWALLETADDRESS4TESTINGPURPOSES9ABCDEFGHIJK";

// Sample policy data for demo
export const MOCK_POLICIES: Map<bigint, PolicyData> = new Map([
  [1n, {
    owner: MOCK_WALLET_ADDRESS,
    zipCode: "90210",
    t0: BigInt(Date.now() - 30 * 24 * 60 * 60 * 1000), // 30 days ago
    t1: BigInt(Date.now() + 30 * 24 * 60 * 60 * 1000), // 30 days from now
    cap: 5000000000n, // 5000 ALGO
    direction: 1n, // Temperature increase
    threshold: 35000n, // 35°C in millidegrees
    slope: 500n,
    feePaid: 150000000n, // 150 ALGO
    settled: 0n // Not settled
  }],
  [2n, {
    owner: MOCK_WALLET_ADDRESS,
    zipCode: "10001",
    t0: BigInt(Date.now() - 60 * 24 * 60 * 60 * 1000), // 60 days ago
    t1: BigInt(Date.now() - 10 * 24 * 60 * 60 * 1000), // 10 days ago (expired)
    cap: 3000000000n, // 3000 ALGO
    direction: 0n, // Temperature decrease
    threshold: 5000n, // 5°C in millidegrees
    slope: 300n,
    feePaid: 90000000n, // 90 ALGO
    settled: 1n // Settled/paid out
  }],
  [3n, {
    owner: MOCK_WALLET_ADDRESS,
    zipCode: "94102", 
    t0: BigInt(Date.now() - 15 * 24 * 60 * 60 * 1000), // 15 days ago
    t1: BigInt(Date.now() + 45 * 24 * 60 * 60 * 1000), // 45 days from now
    cap: 8000000000n, // 8000 ALGO
    direction: 1n, // Temperature increase
    threshold: 40000n, // 40°C in millidegrees
    slope: 800n,
    feePaid: 240000000n, // 240 ALGO
    settled: 0n // Not settled - CLAIMABLE!
  }]
]);

// Sample dispute data for demo
export const MOCK_DISPUTES: Map<bigint, DisputeData> = new Map([
  [1n, {
    policy_id: 3n,
    claimant: MOCK_WALLET_ADDRESS,
    created_at: BigInt(Date.now() - 3 * 24 * 60 * 60 * 1000), // 3 days ago
    resolved: 0n, // Pending
    yes_votes: 2n,
    no_votes: 1n,
    total_votes: 3n,
    reason: "Weather station data shows temperature exceeded 40°C for 5 consecutive days in ZIP 94102",
    voting_deadline: BigInt(Date.now() + 4 * 24 * 60 * 60 * 1000), // 4 days from now
    resolution_round: BigInt(Date.now() + 7 * 24 * 60 * 60 * 1000)
  }],
  [2n, {
    policy_id: 1n,
    claimant: "ANOTHER7USER4ADDRESSFORDEMOPURPOSES9ABCDEFGHIJK2",
    created_at: BigInt(Date.now() - 7 * 24 * 60 * 60 * 1000), // 7 days ago
    resolved: 1n, // Approved
    yes_votes: 4n,
    no_votes: 1n,
    total_votes: 5n,
    reason: "Extreme heat wave in Beverly Hills exceeded policy threshold",
    voting_deadline: BigInt(Date.now() - 1 * 24 * 60 * 60 * 1000), // 1 day ago (expired)
    resolution_round: BigInt(Date.now() - 1 * 24 * 60 * 60 * 1000)
  }]
]);

// Sample juror data
export const MOCK_JUROR_DATA: JurorData = {
  address: MOCK_WALLET_ADDRESS,
  reputation: 85n, // 85% accuracy
  total_votes: 12n,
  correct_votes: 10n,
  registration_round: BigInt(Date.now() - 90 * 24 * 60 * 60 * 1000), // Registered 90 days ago
  last_vote_round: BigInt(Date.now() - 2 * 24 * 60 * 60 * 1000), // Last vote 2 days ago
  staked_amount: 1000000000n // 1000 ALGO staked
};

// Disputes assigned to current juror
export const MOCK_ASSIGNED_DISPUTES = [1n, 3n]; // Can vote on disputes 1 and a new one

// Additional disputes for juror voting
export const MOCK_ADDITIONAL_DISPUTES: Map<bigint, DisputeData> = new Map([
  [3n, {
    policy_id: 2n,
    claimant: "FARMER7CLAIMANT4TESTINGPURPOSES9ABCDEFGHIJK3",
    created_at: BigInt(Date.now() - 1 * 24 * 60 * 60 * 1000), // 1 day ago
    resolved: 0n, // Pending
    yes_votes: 0n,
    no_votes: 0n,
    total_votes: 0n,
    reason: "Crop damage due to unexpected frost in Manhattan area, seeking insurance payout",
    voting_deadline: BigInt(Date.now() + 6 * 24 * 60 * 60 * 1000), // 6 days from now
    resolution_round: BigInt(Date.now() + 9 * 24 * 60 * 60 * 1000)
  }]
]);

// Merge all disputes
export const ALL_MOCK_DISPUTES = new Map([
  ...MOCK_DISPUTES,
  ...MOCK_ADDITIONAL_DISPUTES
]);

// Policy status helper
export function getPolicyStatus(policy: PolicyData): 'Active' | 'Expired' | 'Settled' | 'Claimable' {
  const now = Date.now();
  
  if (policy.settled === 1n) return 'Settled';
  if (policy.t1 < now) return 'Expired';
  
  // For demo purposes, make policy 3 claimable
  if (policy.zipCode === "94102") return 'Claimable';
  
  return 'Active';
}

// Dispute status helper
export function getDisputeStatus(dispute: DisputeData): 'Pending' | 'Approved' | 'Rejected' | 'Voting' {
  if (dispute.resolved === 1n) return 'Approved';
  if (dispute.resolved === 2n) return 'Rejected';
  
  const now = Date.now();
  if (dispute.voting_deadline > now) return 'Voting';
  
  return 'Pending';
}

// Format address for display
export function formatAddress(address: string): string {
  if (!address) return '';
  return `${address.slice(0, 6)}...${address.slice(-4)}`;
}

// Format amount for display
export function formatAlgo(microAlgos: bigint): string {
  return (Number(microAlgos) / 1_000_000).toFixed(2);
}

// Format date for display
export function formatDate(timestamp: bigint | number): string {
  const date = new Date(Number(timestamp));
  return date.toLocaleDateString();
}

// Calculate days remaining
export function getDaysRemaining(futureTimestamp: bigint): number {
  const now = Date.now();
  const diff = Number(futureTimestamp) - now;
  return Math.max(0, Math.ceil(diff / (24 * 60 * 60 * 1000)));
}
