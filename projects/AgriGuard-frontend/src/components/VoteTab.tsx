import React, { useState, useEffect } from 'react'
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  CircularProgress,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  LinearProgress,
  Avatar,
  Divider
} from '@mui/material'
import { styled } from '@mui/material/styles'
import ThumbUpIcon from '@mui/icons-material/ThumbUp'
import ThumbDownIcon from '@mui/icons-material/ThumbDown'
import GavelIcon from '@mui/icons-material/Gavel'
import PersonIcon from '@mui/icons-material/Person'
import AccessTimeIcon from '@mui/icons-material/AccessTime'
import { useWallet } from '@txnlab/use-wallet-react'
import { useSnackbar } from 'notistack'
import { AgriGuardDisputeClientImpl, DisputeClient, DisputeData, JurorData } from '../contracts/AgriGuardDispute'
import { getAlgodConfigFromViteEnvironment, getIndexerConfigFromViteEnvironment } from '../utils/network/getAlgoClientConfigs'
import { AlgorandClient } from '@algorandfoundation/algokit-utils'
import { DEMO_MODE } from '../config/demo'
import { mockDisputeClient } from '../mocks/MockDisputeClient'
import { ALL_MOCK_DISPUTES, MOCK_WALLET_ADDRESS, MOCK_JUROR_DATA, MOCK_ASSIGNED_DISPUTES, formatAddress, formatDate, getDisputeStatus, formatAlgo } from '../mocks/mockData'

// Dispute interfaces matching the contract
interface AssignedDispute {
  disputeId: bigint
  disputeData: DisputeData
  hasVoted: boolean
  userVote?: bigint
}

// Minimalistic styled components
const MinimalCard = styled(Card)({
  backgroundColor: '#ffffff',
  borderRadius: 8,
  border: '1px solid #f0f0f0',
  boxShadow: 'none',
})

const MinimalTable = styled(Table)({
  '& .MuiTableCell-root': {
    borderBottom: '1px solid #f0f0f0',
    padding: '12px 16px',
  },
  '& .MuiTableHead-root .MuiTableCell-root': {
    backgroundColor: '#f8f8f8',
    fontWeight: 600,
    fontSize: '0.875rem',
    color: '#000000',
  },
})

const MinimalButton = styled(Button)({
  borderRadius: 6,
  textTransform: 'none',
  fontWeight: 500,
  fontSize: '0.875rem',
  padding: '6px 16px',
})

const MinimalChip = styled(Chip)({
  borderRadius: 4,
  fontSize: '0.75rem',
  height: 24,
})

const VoteTab: React.FC = () => {
  const { activeAddress, transactionSigner } = useWallet()
  const { enqueueSnackbar } = useSnackbar()

  const [jurorInfo, setJurorInfo] = useState<JurorData | null>(null)
  const [assignedDisputes, setAssignedDisputes] = useState<AssignedDispute[]>([])
  const [loading, setLoading] = useState(false)
  const [votingDisputes, setVotingDisputes] = useState<Set<bigint>>(new Set())
  const [registering, setRegistering] = useState(false)
  const [voteDialogOpen, setVoteDialogOpen] = useState(false)
  const [currentDispute, setCurrentDispute] = useState<AssignedDispute | null>(null)
  const [selectedVote, setSelectedVote] = useState<bigint | null>(null)

  // Fetch juror information and assigned disputes
  const fetchJurorData = async () => {
    if (!activeAddress) return

    setLoading(true)
    try {
      const algodConfig = getAlgodConfigFromViteEnvironment()
      const algorand = AlgorandClient.fromConfig({ algodConfig })

      const disputeClient = new AgriGuardDisputeClientImpl(
        algorand,
        BigInt(import.meta.env.VITE_DISPUTE_APP_ID || '1087'),
        activeAddress
      )

      // Get juror information
      const jurorResponse = await disputeClient.getJurorInfo({ jurorAddress: activeAddress })
      setJurorInfo(jurorResponse.return)

      // Get disputes assigned to this juror
      const disputesResponse = await disputeClient.getJurorAssignedDisputes({
        jurorAddress: activeAddress
      })

      // Parse the returned bytes to extract dispute IDs
      const assignedDisputeIds: bigint[] = []
      const disputeBytes = disputesResponse.return

      // Convert bytes to dispute IDs (simplified parsing)
      if (disputeBytes && disputeBytes.length > 0) {
        for (let i = 0; i < disputeBytes.length; i += 8) { // Each dispute ID is 8 bytes
          if (i + 8 <= disputeBytes.length) {
            const disputeIdBytes = disputeBytes.slice(i, i + 8)
            // Convert bytes to BigInt (simplified)
            let disputeId = BigInt(0)
            for (let j = 0; j < 8; j++) {
              disputeId |= BigInt(disputeBytes.charCodeAt(i + j)) << BigInt(8 * (7 - j))
            }
            if (disputeId > 0) {
              assignedDisputeIds.push(disputeId)
            }
          }
        }
      }

      // Fetch detailed dispute data for each assigned dispute
      const disputesWithDetails: AssignedDispute[] = []
      for (const disputeId of assignedDisputeIds) {
        try {
          const disputeResponse = await disputeClient.getDispute({ disputeId })
          const disputeData = disputeResponse.return

          // Check if user has already voted on this dispute
          const assignmentCheck = await disputeClient.isJurorAssignedToDispute({
            jurorAddress: activeAddress,
            disputeId: disputeId
          })

          const isAssigned = assignmentCheck.return === BigInt(1)

          disputesWithDetails.push({
            disputeId,
            disputeData,
            hasVoted: false, // For now, we'll assume they haven't voted
            userVote: undefined
          })
        } catch (error) {
          console.error(`Error fetching dispute ${disputeId}:`, error)
        }
      }

      setAssignedDisputes(disputesWithDetails)

    } catch (error: any) {
      console.error('Error fetching juror data:', error)
      enqueueSnackbar(`Error loading juror data: ${error.message}`, { variant: 'error' })
    } finally {
      setLoading(false)
    }
  }

  // Register as a juror
  const registerAsJuror = async () => {
    if (!activeAddress) {
      enqueueSnackbar('Please connect your wallet first', { variant: 'error' })
      return
    }

    setRegistering(true)
    try {
      const algodConfig = getAlgodConfigFromViteEnvironment()
      const algorand = AlgorandClient.fromConfig({ algodConfig })

      const disputeClient = new AgriGuardDisputeClientImpl(
        algorand,
        BigInt(import.meta.env.VITE_DISPUTE_APP_ID || '1087'),
        activeAddress
      )

      const response = await disputeClient.registerJuror()
      const result = response.return

      if (result === BigInt(1)) {
        enqueueSnackbar('Successfully registered as a juror!', { variant: 'success' })
        // Refresh juror data
        await fetchJurorData()
      } else {
        enqueueSnackbar('Registration failed - you may already be registered', { variant: 'warning' })
      }

    } catch (error: any) {
      console.error('Error registering juror:', error)
      enqueueSnackbar(`Error registering juror: ${error.message}`, { variant: 'error' })
    } finally {
      setRegistering(false)
    }
  }

  // Vote on a dispute
  const voteOnDispute = async (dispute: AssignedDispute, vote: bigint) => {
    if (!activeAddress) {
      enqueueSnackbar('Please connect your wallet first', { variant: 'error' })
      return
    }

    setVotingDisputes(prev => new Set(prev).add(dispute.disputeId))

    try {
      const algodConfig = getAlgodConfigFromViteEnvironment()
      const algorand = AlgorandClient.fromConfig({ algodConfig })

      const disputeClient = new AgriGuardDisputeClientImpl(
        algorand,
        BigInt(import.meta.env.VITE_DISPUTE_APP_ID || '1087'),
        activeAddress
      )

      const response = await disputeClient.voteOnDispute({
        disputeId: dispute.disputeId,
        vote: vote
      })

      const result = response.return

      if (result === BigInt(1)) {
        const voteText = vote === BigInt(1) ? 'approved' : 'rejected'
        enqueueSnackbar(`Vote submitted successfully! You ${voteText} the dispute.`, { variant: 'success' })

        // Update the dispute in our local state
        setAssignedDisputes(prev => prev.map(d =>
          d.disputeId === dispute.disputeId
            ? { ...d, hasVoted: true, userVote: vote }
            : d
        ))

        // Refresh juror data to update reputation/vote counts
        await fetchJurorData()
      } else {
        enqueueSnackbar('Vote submission failed', { variant: 'error' })
      }

    } catch (error: any) {
      console.error('Error voting on dispute:', error)
      enqueueSnackbar(`Error voting on dispute: ${error.message}`, { variant: 'error' })
    } finally {
      setVotingDisputes(prev => {
        const newSet = new Set(prev)
        newSet.delete(dispute.disputeId)
        return newSet
      })
      setVoteDialogOpen(false)
      setCurrentDispute(null)
      setSelectedVote(null)
    }
  }

  // Open vote dialog
  const openVoteDialog = (dispute: AssignedDispute) => {
    setCurrentDispute(dispute)
    setVoteDialogOpen(true)
  }

  // Close vote dialog
  const closeVoteDialog = () => {
    setVoteDialogOpen(false)
    setCurrentDispute(null)
    setSelectedVote(null)
  }

  // Confirm vote
  const confirmVote = () => {
    if (currentDispute && selectedVote !== null) {
      voteOnDispute(currentDispute, selectedVote)
    }
  }

  // Calculate voting progress
  const calculateVotingProgress = (dispute: DisputeData) => {
    const total = Number(dispute.total_votes)
    const required = 7 // Need at least 7 votes
    return Math.min((total / required) * 100, 100)
  }

  // Get status color
  const getStatusColor = (status: bigint) => {
    switch (status) {
      case BigInt(0): return 'primary' // Active
      case BigInt(1): return 'success' // Approved
      case BigInt(2): return 'error' // Rejected
      default: return 'default'
    }
  }

  // Get status text
  const getStatusText = (status: bigint) => {
    switch (status) {
      case BigInt(0): return 'Active'
      case BigInt(1): return 'Approved'
      case BigInt(2): return 'Rejected'
      default: return 'Unknown'
    }
  }

  useEffect(() => {
    fetchJurorData()
  }, [activeAddress])

  if (!activeAddress) {
    return (
      <Box sx={{ textAlign: 'center', py: 8 }}>
        <PersonIcon sx={{ fontSize: 64, color: '#ccc', mb: 2 }} />
        <Typography variant="h5" color="text.secondary">
          Connect your wallet to participate in dispute resolution
        </Typography>
      </Box>
    )
  }

  return (
    <Box>
      <Typography variant="h4" sx={{ mb: 3, fontWeight: 300 }}>
        Dispute Resolution
      </Typography>

      {/* Juror Status Card */}
      <MinimalCard sx={{ mb: 3 }}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            <Avatar sx={{ mr: 2, bgcolor: '#000000' }}>
              <PersonIcon />
            </Avatar>
            <Box sx={{ flex: 1 }}>
              <Typography variant="h6" sx={{ fontWeight: 500 }}>
                Your Juror Status
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {activeAddress.slice(0, 6)}...{activeAddress.slice(-4)}
              </Typography>
            </Box>
          </Box>

          {jurorInfo ? (
            <Box sx={{ display: 'flex', gap: 3, flexWrap: 'wrap' }}>
              <Box>
                <Typography variant="body2" color="text.secondary">
                  Reputation
                </Typography>
                <Typography variant="h6" sx={{ color: '#000000' }}>
                  {Number(jurorInfo.reputation)} pts
                </Typography>
              </Box>
              <Box>
                <Typography variant="body2" color="text.secondary">
                  Total Votes
                </Typography>
                <Typography variant="h6" sx={{ color: '#000000' }}>
                  {Number(jurorInfo.total_votes)}
                </Typography>
              </Box>
              <Box>
                <Typography variant="body2" color="text.secondary">
                  Correct Votes
                </Typography>
                <Typography variant="h6" sx={{ color: '#000000' }}>
                  {Number(jurorInfo.correct_votes)}
                </Typography>
              </Box>
              <Box>
                <Typography variant="body2" color="text.secondary">
                  Staked Amount
                </Typography>
                <Typography variant="h6" sx={{ color: '#000000' }}>
                  {Number(jurorInfo.staked_amount) / 1000000} ALGO
                </Typography>
              </Box>
            </Box>
          ) : (
            <Box sx={{ textAlign: 'center', py: 2 }}>
              <Typography variant="body1" color="text.secondary" sx={{ mb: 2 }}>
                You are not registered as a juror yet
              </Typography>
              <MinimalButton
                variant="contained"
                onClick={registerAsJuror}
                disabled={registering}
                startIcon={registering ? <CircularProgress size={16} /> : <GavelIcon />}
              >
                {registering ? 'Registering...' : 'Register as Juror'}
              </MinimalButton>
            </Box>
          )}
        </CardContent>
      </MinimalCard>

      {/* Assigned Disputes */}
      <Typography variant="h5" sx={{ mb: 2, fontWeight: 400 }}>
        Disputes Assigned to You
      </Typography>

      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
          <CircularProgress />
        </Box>
      ) : assignedDisputes.length === 0 ? (
        <MinimalCard>
          <CardContent sx={{ textAlign: 'center', py: 6 }}>
            <GavelIcon sx={{ fontSize: 48, color: '#ccc', mb: 2 }} />
            <Typography variant="h6" color="text.secondary">
              No disputes assigned
            </Typography>
            <Typography variant="body2" color="text.secondary">
              You don't have any disputes assigned for voting at the moment.
            </Typography>
          </CardContent>
        </MinimalCard>
      ) : (
        <MinimalCard>
          <TableContainer>
            <MinimalTable>
              <TableHead>
                <TableRow>
                  <TableCell>Dispute ID</TableCell>
                  <TableCell>Policy ID</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Votes</TableCell>
                  <TableCell>Progress</TableCell>
                  <TableCell>Deadline</TableCell>
                  <TableCell>Action</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {assignedDisputes.map((assignedDispute) => {
                  const dispute = assignedDispute.disputeData
                  const progress = calculateVotingProgress(dispute)
                  const isVoting = votingDisputes.has(assignedDispute.disputeId)

                  return (
                    <TableRow key={Number(assignedDispute.disputeId)}>
                      <TableCell>
                        <Typography variant="body2" sx={{ fontWeight: 500 }}>
                          #{Number(assignedDispute.disputeId)}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2">
                          Policy #{Number(dispute.policy_id)}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <MinimalChip
                          label={getStatusText(dispute.resolved)}
                          color={getStatusColor(dispute.resolved)}
                          size="small"
                        />
                      </TableCell>
                      <TableCell>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          <ThumbUpIcon sx={{ color: 'green', fontSize: 16 }} />
                          <Typography variant="body2">
                            {Number(dispute.yes_votes)}
                          </Typography>
                          <ThumbDownIcon sx={{ color: 'red', fontSize: 16, ml: 1 }} />
                          <Typography variant="body2">
                            {Number(dispute.no_votes)}
                          </Typography>
                        </Box>
                      </TableCell>
                      <TableCell sx={{ width: 120 }}>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          <LinearProgress
                            variant="determinate"
                            value={progress}
                            sx={{ flex: 1, height: 6, borderRadius: 3 }}
                          />
                          <Typography variant="body2" sx={{ minWidth: 35 }}>
                            {Math.round(progress)}%
                          </Typography>
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                          <AccessTimeIcon sx={{ fontSize: 14, color: 'text.secondary' }} />
                          <Typography variant="body2" color="text.secondary">
                            Round {Number(dispute.voting_deadline)}
                          </Typography>
                        </Box>
                      </TableCell>
                      <TableCell>
                        {assignedDispute.hasVoted ? (
                          <MinimalChip
                            label={`Voted ${assignedDispute.userVote === BigInt(1) ? 'Yes' : 'No'}`}
                            color="success"
                            size="small"
                          />
                        ) : dispute.resolved === BigInt(0) ? (
                          <MinimalButton
                            variant="outlined"
                            size="small"
                            onClick={() => openVoteDialog(assignedDispute)}
                            disabled={isVoting}
                            startIcon={isVoting ? <CircularProgress size={14} /> : <GavelIcon />}
                          >
                            {isVoting ? 'Voting...' : 'Vote'}
                          </MinimalButton>
                        ) : (
                          <Typography variant="body2" color="text.secondary">
                            Completed
                          </Typography>
                        )}
                      </TableCell>
                    </TableRow>
                  )
                })}
              </TableBody>
            </MinimalTable>
          </TableContainer>
        </MinimalCard>
      )}

      {/* Vote Dialog */}
      <Dialog
        open={voteDialogOpen}
        onClose={closeVoteDialog}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <GavelIcon />
            <Typography variant="h6">
              Vote on Dispute #{currentDispute ? Number(currentDispute.disputeId) : ''}
            </Typography>
          </Box>
        </DialogTitle>
        <DialogContent>
          {currentDispute && (
            <Box>
              <Typography variant="body1" sx={{ mb: 3 }}>
                Policy #{Number(currentDispute.disputeData.policy_id)} settlement dispute
              </Typography>

              <Box sx={{ mb: 3 }}>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                  Current Votes:
                </Typography>
                <Box sx={{ display: 'flex', gap: 3 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <ThumbUpIcon sx={{ color: 'green' }} />
                    <Typography variant="h6" sx={{ color: 'green' }}>
                      {Number(currentDispute.disputeData.yes_votes)}
                    </Typography>
                  </Box>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <ThumbDownIcon sx={{ color: 'red' }} />
                    <Typography variant="h6" sx={{ color: 'red' }}>
                      {Number(currentDispute.disputeData.no_votes)}
                    </Typography>
                  </Box>
                </Box>
              </Box>

              <Divider sx={{ my: 2 }} />

              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                Select your vote:
              </Typography>

              <Box sx={{ display: 'flex', gap: 2 }}>
                <MinimalButton
                  variant={selectedVote === BigInt(1) ? "contained" : "outlined"}
                  onClick={() => setSelectedVote(BigInt(1))}
                  startIcon={<ThumbUpIcon />}
                  sx={{
                    flex: 1,
                    py: 2,
                    backgroundColor: selectedVote === BigInt(1) ? '#4caf50' : 'transparent',
                    color: selectedVote === BigInt(1) ? 'white' : '#4caf50',
                    borderColor: '#4caf50',
                    '&:hover': {
                      backgroundColor: selectedVote === BigInt(1) ? '#45a049' : 'rgba(76, 175, 80, 0.04)',
                    }
                  }}
                >
                  Approve Payout
                </MinimalButton>

                <MinimalButton
                  variant={selectedVote === BigInt(0) ? "contained" : "outlined"}
                  onClick={() => setSelectedVote(BigInt(0))}
                  startIcon={<ThumbDownIcon />}
                  sx={{
                    flex: 1,
                    py: 2,
                    backgroundColor: selectedVote === BigInt(0) ? '#f44336' : 'transparent',
                    color: selectedVote === BigInt(0) ? 'white' : '#f44336',
                    borderColor: '#f44336',
                    '&:hover': {
                      backgroundColor: selectedVote === BigInt(0) ? '#d32f2f' : 'rgba(244, 67, 54, 0.04)',
                    }
                  }}
                >
                  Reject Claim
                </MinimalButton>
              </Box>

              <Alert severity="info" sx={{ mt: 3 }}>
                <Typography variant="body2">
                  Your vote contributes to the community decision. Make sure to review the dispute details carefully.
                </Typography>
              </Alert>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={closeVoteDialog} color="inherit">
            Cancel
          </Button>
          <Button
            onClick={confirmVote}
            variant="contained"
            disabled={selectedVote === null}
            sx={{
              backgroundColor: '#000000',
              '&:hover': { backgroundColor: '#333333' }
            }}
          >
            Submit Vote
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}

export default VoteTab
