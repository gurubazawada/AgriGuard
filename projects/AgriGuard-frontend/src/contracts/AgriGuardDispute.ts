import { type AlgorandClient } from '@algorandfoundation/algokit-utils/types/algorand-client'

export interface DisputeData {
  policy_id: bigint
  claimant: string
  created_at: bigint
  resolved: bigint  // 0 = pending/active, 1 = approved, 2 = rejected
  yes_votes: bigint
  no_votes: bigint
  total_votes: bigint
}

export interface DisputeClient {
  createDispute(args: { policyId: bigint }): Promise<{ return: bigint }>
  getDispute(args: { disputeId: bigint }): Promise<{ return: DisputeData }>
  registerJuror(): Promise<{ return: bigint }>
}

export class AgriGuardDisputeClientImpl implements DisputeClient {
  private algorand: AlgorandClient
  private appId: bigint
  private defaultSender: string

  constructor(algorand: AlgorandClient, appId: bigint, defaultSender: string) {
    this.algorand = algorand
    this.appId = appId
    this.defaultSender = defaultSender
  }

  async createDispute({ policyId }: { policyId: bigint }): Promise<{ return: bigint }> {
    try {
      // For now, simulate a successful dispute creation
      // In production, this would call the actual dispute contract
      console.log(`Creating dispute for policy ${policyId} with contract ${this.appId}`)
      const disputeId = BigInt(Math.floor(Math.random() * 1000000) + 1)
      return { return: disputeId }
    } catch (error) {
      console.error('Error creating dispute:', error)
      throw error
    }
  }

  async getDispute({ disputeId }: { disputeId: bigint }): Promise<{ return: DisputeData }> {
    try {
      // For now, return mock dispute data
      // In production, this would query the actual dispute contract
      console.log(`Getting dispute ${disputeId} from contract ${this.appId}`)
      return {
        return: {
          policy_id: BigInt(1),
          claimant: this.defaultSender,
          created_at: BigInt(Math.floor(Date.now() / 1000)),
          resolved: BigInt(0), // 0 = pending/active
          yes_votes: BigInt(0),
          no_votes: BigInt(0),
          total_votes: BigInt(0),
        }
      }
    } catch (error) {
      console.error('Error getting dispute:', error)
      throw error
    }
  }

  async registerJuror(): Promise<{ return: bigint }> {
    try {
      // For now, simulate successful juror registration
      // In production, this would call the actual dispute contract
      console.log(`Registering juror ${this.defaultSender} with contract ${this.appId}`)
      return { return: BigInt(1) } // Success
    } catch (error) {
      console.error('Error registering juror:', error)
      throw error
    }
  }
}

// Factory class for creating dispute clients
export class AgriGuardDisputeFactory {
  private algorand: AlgorandClient
  private defaultSender?: string

  constructor(params: {
    algorand: AlgorandClient
    defaultSender?: string
  }) {
    this.algorand = params.algorand
    this.defaultSender = params.defaultSender
  }

  getAppClientById(params: { appId: bigint }): AgriGuardDisputeClientImpl {
    return new AgriGuardDisputeClientImpl(
      this.algorand,
      params.appId,
      this.defaultSender || ''
    )
  }
}
