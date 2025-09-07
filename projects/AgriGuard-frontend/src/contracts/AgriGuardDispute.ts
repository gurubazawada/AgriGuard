import { type AlgorandClient, type AppClient } from '@algorandfoundation/algokit-utils/types/app-client'

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

export interface VoteData {
  juror: string
  vote: bigint  // 0 = no, 1 = yes
  timestamp: bigint
  dispute_id: bigint
}

export interface DisputeClient {
  createDispute(args: { policyId: bigint }): Promise<{ return: bigint }>
  getDispute(args: { disputeId: bigint }): Promise<{ return: DisputeData }>
  registerJuror(): Promise<{ return: bigint }>
  getJurorInfo(args: { jurorAddress: string }): Promise<{ return: JurorData }>
  voteOnDispute(args: { disputeId: bigint, vote: bigint }): Promise<{ return: bigint }>
  getDisputesAssignedToJuror(args: { jurorAddress: string }): Promise<{ return: bigint[] }>
  getDisputeStatus(args: { disputeId: bigint }): Promise<{ return: bigint }>
  getJurorAssignedDisputes(args: { jurorAddress: string }): Promise<{ return: string }>
  isJurorAssignedToDispute(args: { jurorAddress: string, disputeId: bigint }): Promise<{ return: bigint }>
}

export class AgriGuardDisputeClientImpl implements DisputeClient {
  private algorand: AlgorandClient
  private appId: bigint
  private defaultSender: string
  private appClient: AppClient | null = null

  constructor(algorand: AlgorandClient, appId: bigint, defaultSender: string) {
    this.algorand = algorand
    this.appId = appId
    this.defaultSender = defaultSender
  }

  private async getAppClient(): Promise<AppClient> {
    if (!this.appClient) {
      // Create app spec for the dispute contract
      // This would normally be imported from the generated client
      const appSpec = {
        // This would be the actual app spec from the compiled contract
        // For now, we'll use a basic implementation
      }

      this.appClient = this.algorand.client.app({
        appId: this.appId,
        appSpec: appSpec as any,
        sender: this.defaultSender,
      })
    }
    return this.appClient
  }

  async createDispute({ policyId }: { policyId: bigint }): Promise<{ return: bigint }> {
    try {
      const appClient = await this.getAppClient()
      console.log(`Creating dispute for policy ${policyId} with contract ${this.appId}`)

      // Call the create_dispute method
      const result = await appClient.call({
        method: 'create_dispute',
        methodArgs: {
          policy_id: policyId
        }
      })

      return { return: result.return as bigint }
    } catch (error) {
      console.error('Error creating dispute:', error)
      throw error
    }
  }

  async getDispute({ disputeId }: { disputeId: bigint }): Promise<{ return: DisputeData }> {
    try {
      const appClient = await this.getAppClient()
      console.log(`Getting dispute ${disputeId} from contract ${this.appId}`)

      // Call the get_dispute method
      const result = await appClient.call({
        method: 'get_dispute',
        methodArgs: {
          dispute_id: disputeId
        }
      })

      const disputeData = result.return as any
      return {
        return: {
          policy_id: disputeData.policy_id,
          claimant: disputeData.claimant,
          created_at: disputeData.created_at,
          resolved: disputeData.status, // Map status to resolved
          yes_votes: disputeData.yes_votes,
          no_votes: disputeData.no_votes,
          total_votes: disputeData.total_votes,
          reason: disputeData.reason || 'Policy settlement dispute',
          voting_deadline: disputeData.voting_deadline,
          resolution_round: disputeData.resolution_round
        }
      }
    } catch (error) {
      console.error('Error getting dispute:', error)
      throw error
    }
  }

  async registerJuror(): Promise<{ return: bigint }> {
    try {
      const appClient = await this.getAppClient()
      console.log(`Registering juror ${this.defaultSender} with contract ${this.appId}`)

      // Call the register_juror method
      const result = await appClient.call({
        method: 'register_juror',
        methodArgs: {}
      })

      return { return: result.return as bigint }
    } catch (error) {
      console.error('Error registering juror:', error)
      throw error
    }
  }

  async getJurorInfo({ jurorAddress }: { jurorAddress: string }): Promise<{ return: JurorData }> {
    try {
      const appClient = await this.getAppClient()

      // Call the get_juror_info method
      const result = await appClient.call({
        method: 'get_juror_info',
        methodArgs: {
          juror_address: jurorAddress
        }
      })

      const jurorData = result.return as any
      return {
        return: {
          address: jurorData.address || jurorAddress,
          reputation: jurorData.reputation || BigInt(100),
          total_votes: jurorData.total_votes || BigInt(0),
          correct_votes: jurorData.correct_votes || BigInt(0),
          registration_round: jurorData.registration_round || BigInt(0),
          last_vote_round: jurorData.last_vote_round || BigInt(0),
          staked_amount: jurorData.staked_amount || BigInt(1000000)
        }
      }
    } catch (error) {
      console.error('Error getting juror info:', error)
      throw error
    }
  }

  async voteOnDispute({ disputeId, vote }: { disputeId: bigint, vote: bigint }): Promise<{ return: bigint }> {
    try {
      const appClient = await this.getAppClient()
      console.log(`Voting on dispute ${disputeId} with vote ${vote}`)

      // Call the vote_on_dispute method
      const result = await appClient.call({
        method: 'vote_on_dispute',
        methodArgs: {
          dispute_id: disputeId,
          vote: vote
        }
      })

      return { return: result.return as bigint }
    } catch (error) {
      console.error('Error voting on dispute:', error)
      throw error
    }
  }

  async getDisputesAssignedToJuror({ jurorAddress }: { jurorAddress: string }): Promise<{ return: bigint[] }> {
    try {
      const appClient = await this.getAppClient()

      // This is a simplified implementation
      // In reality, you'd need to query the dispute_jurors mapping
      // For now, return an empty array as this requires more complex logic
      console.log(`Getting disputes assigned to juror ${jurorAddress}`)

      // Call get_active_disputes to get all active disputes
      const activeDisputesResult = await appClient.call({
        method: 'get_active_disputes',
        methodArgs: {}
      })

      // This would need to be filtered by juror assignment
      // For now, return a sample array
      return { return: [BigInt(1), BigInt(2)] } // Sample dispute IDs
    } catch (error) {
      console.error('Error getting disputes assigned to juror:', error)
      throw error
    }
  }

  async getDisputeStatus({ disputeId }: { disputeId: bigint }): Promise<{ return: bigint }> {
    try {
      const appClient = await this.getAppClient()

      // Call the get_dispute_status method
      const result = await appClient.call({
        method: 'get_dispute_status',
        methodArgs: {
          dispute_id: disputeId
        }
      })

      return { return: result.return as bigint }
    } catch (error) {
      console.error('Error getting dispute status:', error)
      throw error
    }
  }

  async getJurorAssignedDisputes({ jurorAddress }: { jurorAddress: string }): Promise<{ return: string }> {
    try {
      const appClient = await this.getAppClient()

      // Call the get_juror_assigned_disputes method
      const result = await appClient.call({
        method: 'get_juror_assigned_disputes',
        methodArgs: {
          juror_address: jurorAddress
        }
      })

      return { return: result.return as string }
    } catch (error) {
      console.error('Error getting juror assigned disputes:', error)
      throw error
    }
  }

  async isJurorAssignedToDispute({ jurorAddress, disputeId }: { jurorAddress: string, disputeId: bigint }): Promise<{ return: bigint }> {
    try {
      const appClient = await this.getAppClient()

      // Call the is_juror_assigned_to_dispute method
      const result = await appClient.call({
        method: 'is_juror_assigned_to_dispute',
        methodArgs: {
          juror_address: jurorAddress,
          dispute_id: disputeId
        }
      })

      return { return: result.return as bigint }
    } catch (error) {
      console.error('Error checking juror assignment:', error)
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
