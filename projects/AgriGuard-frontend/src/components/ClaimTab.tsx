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
  Collapse,
  IconButton,
  Chip,
  Tooltip,
  Divider,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  List,
  ListItem,
  ListItemText,
  ListItemIcon
} from '@mui/material'
import { styled } from '@mui/material/styles'
import ExpandMoreIcon from '@mui/icons-material/ExpandMore'
import ExpandLessIcon from '@mui/icons-material/ExpandLess'
import InfoIcon from '@mui/icons-material/Info'
import CheckCircleIcon from '@mui/icons-material/CheckCircle'
import CancelIcon from '@mui/icons-material/Cancel'
import GavelIcon from '@mui/icons-material/Gavel'
import { useWallet } from '@txnlab/use-wallet-react'
import { useSnackbar } from 'notistack'
import { AgriGuardInsuranceFactory } from '../contracts/AgriGuardInsurance'
import { AgriGuardDisputeClientImpl, DisputeClient } from '../contracts/AgriGuardDispute'
import { getAlgodConfigFromViteEnvironment, getIndexerConfigFromViteEnvironment } from '../utils/network/getAlgoClientConfigs'
import { AlgorandClient } from '@algorandfoundation/algokit-utils'

// Dispute contract interfaces (matches the contract client)
interface DisputeData {
  policy_id: bigint
  claimant: string
  created_at: bigint
  resolved: bigint  // 0 = pending/active, 1 = approved, 2 = rejected
  yes_votes: bigint
  no_votes: bigint
  total_votes: bigint
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

interface Policy {
  id: number
  owner: string
  zipCode: string
  t0: bigint
  t1: bigint
  cap: bigint
  status: string
}

interface ClaimResult {
  decision: number
  reasoning: string
  reasoning_steps: string[]
  web_sources: string[]
  confidence: number
  settlement_amount: number
  transaction_id: string
  transaction_success: boolean
}

const ClaimTab: React.FC = () => {
  const { activeAddress, transactionSigner } = useWallet()
  const { enqueueSnackbar } = useSnackbar()
  
  const [policies, setPolicies] = useState<Policy[]>([])
  const [loading, setLoading] = useState(false)
  const [claimingPolicies, setClaimingPolicies] = useState<Set<number>>(new Set())
  const [claimResults, setClaimResults] = useState<Map<number, ClaimResult>>(new Map())
  const [expandedClaims, setExpandedClaims] = useState<Set<number>>(new Set())
  const [disputingPolicies, setDisputingPolicies] = useState<Set<number>>(new Set())
  const [disputes, setDisputes] = useState<Map<number, DisputeData>>(new Map())
  const [claimModalOpen, setClaimModalOpen] = useState(false)
  const [currentClaimResult, setCurrentClaimResult] = useState<ClaimResult | null>(null)
  const [currentPolicyId, setCurrentPolicyId] = useState<number | null>(null)

  const fetchPolicies = async () => {
    if (!activeAddress) return

    setLoading(true)
    try {
      const algodConfig = getAlgodConfigFromViteEnvironment()
      const indexerConfig = getIndexerConfigFromViteEnvironment()
      
      const algorand = AlgorandClient.fromConfig({ algodConfig })

      const appFactory = new AgriGuardInsuranceFactory({
        defaultSender: activeAddress ?? undefined,
        algorand,
      })

      const appClient = appFactory.getAppClientById({
        appId: BigInt(import.meta.env.VITE_APP_ID || '1061'),
      })

      const totalPoliciesResponse = await appClient.getPolicyCount()
      const totalPolicies = Number(totalPoliciesResponse)

      const policiesByOwnerResponse = await appClient.getPoliciesByOwner({ args: [activeAddress] })
      const policiesByOwner = policiesByOwnerResponse as [bigint, bigint]

      const policiesList: Policy[] = []
      for (let i = 0; i < policiesByOwner[0]; i++) {
        const policyId = Number(policiesByOwner[1] + BigInt(i))
        const policyResponse = await appClient.getPolicy({ args: [policyId] })
        const policyData = policyResponse as any

        policiesList.push({
          id: policyId,
          owner: policyData.owner,
          zipCode: policyData.zipCode,
          t0: policyData.t0,
          t1: policyData.t1,
          cap: policyData.cap,
          status: policyData.settled ? 'settled' : 'active'
        })
      }

      setPolicies(policiesList)
    } catch (error) {
      console.error('Error fetching policies:', error)
      enqueueSnackbar('Failed to fetch policies', { variant: 'error' })
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchPolicies()
  }, [activeAddress])

  const fileClaim = async (policy: Policy) => {
    if (!activeAddress) {
      enqueueSnackbar('Please connect your wallet first', { variant: 'error' })
      return
    }

    setClaimingPolicies(prev => new Set(prev).add(policy.id))

    try {
      const response = await fetch('http://localhost:8000/oracle-settle', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          policy_id: policy.id,
          zip_code: policy.zipCode,
          start_date: new Date(Number(policy.t0) * 1000).toISOString().split('T')[0],
          end_date: new Date(Number(policy.t1) * 1000).toISOString().split('T')[0],
          coverage_amount: String(Number(policy.cap) / 1000000), // Convert from microALGO to ALGO
          direction: 0, // Default direction
          threshold: 5000, // Default threshold
          slope: 100, // Default slope
          fee_paid: 0, // Default fee paid
          settled: false, // Default not settled
          owner: policy.owner // Add missing owner field
        }),
      })

      if (!response.ok) {
        throw new Error('Claim failed')
      }

      const result = await response.json()
      setClaimResults(prev => new Map(prev).set(policy.id, result))
      
      // Show the claim result in a modal
      setCurrentClaimResult(result)
      setCurrentPolicyId(policy.id)
      setClaimModalOpen(true)
    } catch (error: any) {
      console.error('Error filing claim:', error)
      enqueueSnackbar(`Claim failed: ${error.message}`, { variant: 'error' })
    } finally {
      setClaimingPolicies(prev => {
        const newSet = new Set(prev)
        newSet.delete(policy.id)
        return newSet
      })
    }
  }

  const createDispute = async (policy: Policy) => {
    if (!activeAddress) {
      enqueueSnackbar('Please connect your wallet first', { variant: 'error' })
      return
    }

    setDisputingPolicies(prev => new Set(prev).add(policy.id))

    try {
      const algodConfig = getAlgodConfigFromViteEnvironment()
      const indexerConfig = getIndexerConfigFromViteEnvironment()
      
      const algorand = AlgorandClient.fromConfig({ algodConfig })

      const disputeClient = new AgriGuardDisputeClientImpl(
        algorand,
        BigInt(import.meta.env.VITE_DISPUTE_APP_ID || '1087'),
        activeAddress
      )

      const response = await disputeClient.createDispute({ policyId: BigInt(policy.id) })
      const disputeId = response.return

      const disputeResponse = await disputeClient.getDispute({ disputeId: disputeId })
      const disputeData = disputeResponse.return

      setDisputes(prev => new Map(prev).set(policy.id, disputeData))

      enqueueSnackbar(`Dispute created successfully! Dispute ID: ${disputeId}`, { variant: 'success' })

    } catch (error: any) {
      console.error('Error creating dispute:', error)
      enqueueSnackbar(`Error creating dispute: ${error.message}`, { variant: 'error' })
    } finally {
      setDisputingPolicies(prev => {
        const newSet = new Set(prev)
        newSet.delete(policy.id)
        return newSet
      })
    }
  }

  const toggleClaimExpansion = (policyId: number) => {
    setExpandedClaims(prev => {
      const newSet = new Set(prev)
      if (newSet.has(policyId)) {
        newSet.delete(policyId)
      } else {
        newSet.add(policyId)
      }
      return newSet
    })
  }

  const handleCloseClaimModal = () => {
    setClaimModalOpen(false)
    setCurrentClaimResult(null)
    setCurrentPolicyId(null)
  }

  const handleDisputeFromModal = async () => {
    if (currentPolicyId) {
      const policy = policies.find(p => p.id === currentPolicyId)
      if (policy) {
        await createDispute(policy)
        handleCloseClaimModal()
      }
    }
  }

  const formatDate = (timestamp: bigint) => {
    return new Date(Number(timestamp) * 1000).toLocaleDateString()
  }

  const formatAmount = (amount: bigint) => {
    return (Number(amount) / 1000000).toFixed(2)
  }

  const getStatusChip = (status: string) => {
    const statusConfig = {
      active: { label: 'Active', color: 'default' as const },
      settled: { label: 'Settled', color: 'success' as const },
    }
    
    const config = statusConfig[status as keyof typeof statusConfig] || { label: status, color: 'default' as const }
    
    return (
      <MinimalChip
        label={config.label}
        color={config.color}
        size="small"
      />
    )
  }

  if (!activeAddress) {
    return (
      <Box sx={{ textAlign: 'center', py: 8 }}>
        <Typography variant="h6" color="text.secondary" sx={{ mb: 2 }}>
          Connect your wallet to view policies
        </Typography>
        <Typography variant="body2" color="text.secondary">
          You need to connect your wallet to see your insurance policies and file claims.
        </Typography>
      </Box>
    )
  }

  return (
    <Box sx={{ maxWidth: 1200, mx: 'auto', p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
        <Typography variant="h4" sx={{ fontWeight: 300 }}>
          Your Policies
        </Typography>
        <Button
          variant="outlined"
          onClick={fetchPolicies}
          disabled={loading}
          sx={{
            borderColor: '#e0e0e0',
            color: '#666666',
            '&:hover': {
              borderColor: '#b0b0b0',
              backgroundColor: '#f5f5f5',
            },
          }}
        >
          {loading ? 'Refreshing...' : 'Refresh'}
        </Button>
      </Box>

      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
          <CircularProgress />
        </Box>
      ) : policies.length === 0 ? (
        <Box sx={{ textAlign: 'center', py: 8 }}>
          <Typography variant="h6" color="text.secondary" sx={{ mb: 2 }}>
            No policies found
          </Typography>
          <Typography variant="body2" color="text.secondary">
            You don't have any insurance policies yet. Create one in the Policy tab.
          </Typography>
        </Box>
      ) : (
        <MinimalCard>
          <TableContainer>
            <MinimalTable>
              <TableHead>
                <TableRow>
                  <TableCell>Policy ID</TableCell>
                  <TableCell>ZIP Code</TableCell>
                  <TableCell>Coverage Period</TableCell>
                  <TableCell>Coverage Amount</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell align="center">Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {policies.map((policy) => (
                  <React.Fragment key={policy.id}>
                    <TableRow>
                      <TableCell>
                        <Typography variant="body2" sx={{ fontWeight: 500 }}>
                          #{policy.id}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2">
                          {policy.zipCode}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2">
                          {formatDate(policy.t0)} - {formatDate(policy.t1)}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2">
                          {formatAmount(policy.cap)} ALGO
                        </Typography>
                      </TableCell>
                      <TableCell>
                        {getStatusChip(policy.status)}
                      </TableCell>
                      <TableCell align="center">
                        {policy.status === 'active' && (
                          <MinimalButton
                            variant="contained"
                            onClick={() => fileClaim(policy)}
                            disabled={claimingPolicies.has(policy.id)}
                            sx={{
                              backgroundColor: '#000000',
                              color: '#ffffff',
                              '&:hover': {
                                backgroundColor: '#333333',
                              },
                            }}
                          >
                            {claimingPolicies.has(policy.id) ? 'Filing...' : 'File Claim'}
                          </MinimalButton>
                        )}
                        {policy.status === 'settled' && claimResults.has(policy.id) && (
                          <>
                            <MinimalButton
                              variant="outlined"
                              onClick={() => toggleClaimExpansion(policy.id)}
                              endIcon={expandedClaims.has(policy.id) ? <ExpandLessIcon /> : <ExpandMoreIcon />}
                              sx={{
                                borderColor: '#e0e0e0',
                                color: '#666666',
                                mr: 1,
                                '&:hover': {
                                  borderColor: '#b0b0b0',
                                  backgroundColor: '#f5f5f5',
                                },
                              }}
                            >
                              {expandedClaims.has(policy.id) ? 'Hide' : 'View'} Result
                            </MinimalButton>
                            {(() => {
                              const result = claimResults.get(policy.id)!
                              const isDenied = result.decision === 0
                              const hasDispute = disputes.has(policy.id)
                              
                              if (isDenied && !hasDispute) {
                                return (
                                  <MinimalButton
                                    variant="contained"
                                    onClick={() => createDispute(policy)}
                                    disabled={disputingPolicies.has(policy.id)}
                                    sx={{
                                      backgroundColor: '#f57c00',
                                      color: '#ffffff',
                                      '&:hover': {
                                        backgroundColor: '#ef6c00',
                                      },
                                    }}
                                  >
                                    {disputingPolicies.has(policy.id) ? 'Creating...' : 'Dispute'}
                                  </MinimalButton>
                                )
                              } else if (hasDispute) {
                                const dispute = disputes.get(policy.id)!
                                return (
                                  <MinimalChip
                                    label={`Dispute ${dispute.resolved === 0n ? 'Active' : dispute.resolved === 1n ? 'Approved' : 'Rejected'}`}
                                    color={dispute.resolved === 0n ? 'warning' : dispute.resolved === 1n ? 'success' : 'error'}
                                    size="small"
                                  />
                                )
                              }
                              return null
                            })()}
                          </>
                        )}
                      </TableCell>
                    </TableRow>
                    {policy.status === 'settled' && claimResults.has(policy.id) && expandedClaims.has(policy.id) && (
                      <TableRow>
                        <TableCell colSpan={6} sx={{ py: 0 }}>
                          <Collapse in={expandedClaims.has(policy.id)} timeout="auto" unmountOnExit>
                            <Box sx={{ p: 3, backgroundColor: '#f8f8f8' }}>
                              {(() => {
                                const result = claimResults.get(policy.id)!
                                return (
                                  <Box>
                                    <Typography variant="h6" sx={{ mb: 2, fontWeight: 500 }}>
                                      Claim Result: {result.decision === 1 ? 'Approved' : 'Denied'}
                                    </Typography>
                                    <Typography variant="body2" sx={{ mb: 2 }}>
                                      {result.reasoning}
                                    </Typography>
                                    <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                                      Confidence: {(result.confidence * 100).toFixed(1)}%
                                    </Typography>
                                    {result.settlement_amount > 0 && (
                                      <Typography variant="body2" color="text.secondary">
                                        Settlement Amount: {result.settlement_amount.toFixed(2)} ALGO
                                      </Typography>
                                    )}
                                  </Box>
                                )
                              })()}
                            </Box>
                          </Collapse>
                        </TableCell>
                      </TableRow>
                    )}
                  </React.Fragment>
                ))}
              </TableBody>
            </MinimalTable>
          </TableContainer>
        </MinimalCard>
      )}

      {/* Claim Result Modal */}
      <Dialog 
        open={claimModalOpen} 
        onClose={handleCloseClaimModal}
        maxWidth="md"
        fullWidth
        PaperProps={{
          sx: {
            borderRadius: 3,
            boxShadow: '0 8px 32px rgba(0, 0, 0, 0.12)',
          }
        }}
      >
        <DialogTitle sx={{ 
          textAlign: 'center', 
          pb: 1,
          backgroundColor: currentClaimResult?.decision === 1 ? 'rgba(76, 175, 80, 0.1)' : 'rgba(244, 67, 54, 0.1)',
          borderBottom: `2px solid ${currentClaimResult?.decision === 1 ? '#4caf50' : '#f44336'}`
        }}>
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 2 }}>
            {currentClaimResult?.decision === 1 ? (
              <CheckCircleIcon sx={{ color: '#4caf50', fontSize: 32 }} />
            ) : (
              <CancelIcon sx={{ color: '#f44336', fontSize: 32 }} />
            )}
            <Typography variant="h5" sx={{ 
              fontWeight: 600,
              color: currentClaimResult?.decision === 1 ? '#4caf50' : '#f44336'
            }}>
              Claim {currentClaimResult?.decision === 1 ? 'Approved' : 'Denied'}
            </Typography>
          </Box>
        </DialogTitle>
        
        <DialogContent sx={{ pt: 3 }}>
          {currentClaimResult && (
            <Box>
              {/* Decision Summary */}
              <Box sx={{ 
                p: 3, 
                backgroundColor: currentClaimResult.decision === 1 ? 'rgba(76, 175, 80, 0.05)' : 'rgba(244, 67, 54, 0.05)',
                borderRadius: 2,
                mb: 3,
                border: `1px solid ${currentClaimResult.decision === 1 ? '#4caf50' : '#f44336'}20`
              }}>
                <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
                  Decision Summary
                </Typography>
                <Typography variant="body1" sx={{ mb: 2 }}>
                  {currentClaimResult.reasoning}
                </Typography>
                <Box sx={{ display: 'flex', gap: 3, flexWrap: 'wrap' }}>
                  <Typography variant="body2" color="text.secondary">
                    <strong>Confidence:</strong> {(currentClaimResult.confidence * 100).toFixed(1)}%
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    <strong>Settlement Amount:</strong> {currentClaimResult.settlement_amount ? (Number(currentClaimResult.settlement_amount) / 1000000).toFixed(2) : '0'} ALGO
                  </Typography>
                </Box>
              </Box>

              {/* AI Analysis Steps */}
              {currentClaimResult.reasoning_steps && currentClaimResult.reasoning_steps.length > 0 && (
                <Box sx={{ mb: 3 }}>
                  <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
                    AI Analysis Process
                  </Typography>
                  <List sx={{ backgroundColor: '#f8f9fa', borderRadius: 2, p: 1 }}>
                    {currentClaimResult.reasoning_steps.map((step, index) => (
                      <ListItem key={index} sx={{ py: 0.5 }}>
                        <ListItemIcon sx={{ minWidth: 32 }}>
                          <Typography variant="body2" sx={{ 
                            fontWeight: 600, 
                            color: '#1976d2',
                            minWidth: 20
                          }}>
                            {index + 1}.
                          </Typography>
                        </ListItemIcon>
                        <ListItemText 
                          primary={step}
                          primaryTypographyProps={{ variant: 'body2' }}
                        />
                      </ListItem>
                    ))}
                  </List>
                </Box>
              )}

              {/* Web Sources */}
              {currentClaimResult.web_sources && currentClaimResult.web_sources.length > 0 && (
                <Box sx={{ mb: 3 }}>
                  <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
                    Data Sources
                  </Typography>
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                    {currentClaimResult.web_sources.map((source, index) => (
                      <Chip 
                        key={index}
                        label={source}
                        size="small"
                        variant="outlined"
                        sx={{ 
                          backgroundColor: 'rgba(25, 118, 210, 0.05)',
                          borderColor: '#1976d2',
                          color: '#1976d2'
                        }}
                      />
                    ))}
                  </Box>
                </Box>
              )}
            </Box>
          )}
        </DialogContent>
        
        <DialogActions sx={{ p: 3, gap: 2 }}>
          <Button 
            onClick={handleCloseClaimModal}
            variant="outlined"
            sx={{ borderRadius: 2 }}
          >
            Close
          </Button>
          {currentClaimResult?.decision === 0 && (
            <Button 
              onClick={handleDisputeFromModal}
              variant="contained"
              startIcon={<GavelIcon />}
              sx={{ 
                borderRadius: 2,
                backgroundColor: '#ff9800',
                '&:hover': {
                  backgroundColor: '#f57c00',
                }
              }}
            >
              Dispute Decision
            </Button>
          )}
        </DialogActions>
      </Dialog>
    </Box>
  )
}

export default ClaimTab