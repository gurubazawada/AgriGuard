import React, { useState, useEffect } from 'react'
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Chip,
  Button,
  Alert,
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
  Accordion,
  AccordionSummary,
  AccordionDetails
} from '@mui/material'
import ExpandMoreIcon from '@mui/icons-material/ExpandMore'
import ExpandLessIcon from '@mui/icons-material/ExpandLess'
import InfoIcon from '@mui/icons-material/Info'
import { useWallet } from '@txnlab/use-wallet-react'
import { useSnackbar } from 'notistack'
import { AgriGuardInsuranceFactory } from '../contracts/AgriGuardInsurance'
import { getAlgodConfigFromViteEnvironment, getIndexerConfigFromViteEnvironment } from '../utils/network/getAlgoClientConfigs'
import { AlgorandClient } from '@algorandfoundation/algokit-utils'

interface Policy {
  id: number
  zipCode: string
  startDate: string
  endDate: string
  coverageAmount: string
  fee: string
  status: 'active' | 'settled' | 'expired'
  settled: boolean
  owner: string
  direction: number
  threshold: number
  slope: number
  feePaid: number
}

interface ClaimResult {
  decision: number
  reasoning: string
  reasoning_steps: string[]
  web_sources: string[]
  confidence: number
  settlement_amount: number
  transaction_success: boolean
  transaction_id?: string
}

const ClaimTab: React.FC = () => {
  const { activeAddress, transactionSigner } = useWallet()
  const { enqueueSnackbar } = useSnackbar()
  const [policies, setPolicies] = useState<Policy[]>([])
  const [loading, setLoading] = useState(false)
  const [claimingPolicies, setClaimingPolicies] = useState<Set<number>>(new Set())
  const [claimResults, setClaimResults] = useState<Map<number, ClaimResult>>(new Map())
  const [expandedClaims, setExpandedClaims] = useState<Set<number>>(new Set())

  const algodConfig = getAlgodConfigFromViteEnvironment()
  const indexerConfig = getIndexerConfigFromViteEnvironment()
  const algorand = AlgorandClient.fromConfig({
    algodConfig,
    indexerConfig,
  })
  
  // Set the default signer for the algorand client
  if (transactionSigner) {
    algorand.setDefaultSigner(transactionSigner)
  }

  const fetchPolicies = async () => {
    if (!activeAddress || !transactionSigner) {
      enqueueSnackbar('Please connect your wallet', { variant: 'error' })
      return
    }

    setLoading(true)
    try {
      const factory = new AgriGuardInsuranceFactory({
        defaultSender: activeAddress,
        algorand,
      })

      const appClient = factory.getAppClientById({
        appId: BigInt(import.meta.env.VITE_APP_ID)
      })

      // First, let's check what methods are available and test basic connectivity
      console.log('Testing contract connection...')
      
      // Test basic contract methods
      try {
        const globalsResponse = await appClient.send.getGlobals({ args: [] })
        console.log('Contract globals:', globalsResponse.return)
        
        const countResponse = await appClient.send.getPolicyCount({ args: [] })
        console.log('Policy count response:', countResponse)
        const policyCount = countResponse.return || 0
        console.log('Total policies:', policyCount)

        if (policyCount === 0) {
          setPolicies([])
          enqueueSnackbar('No policies found', { variant: 'info' })
          return
        }

        // Try to get policies by owner
        console.log('Active address for policy lookup:', activeAddress)
        const policiesResponse = await appClient.send.getPoliciesByOwner({
          args: [activeAddress]
        })
        console.log('Policies by owner response:', policiesResponse)
        console.log('Policies by owner return value:', policiesResponse.return)
        console.log('Policies by owner return type:', typeof policiesResponse.return)
        console.log('Policies by owner return length:', policiesResponse.return ? policiesResponse.return.length : 'undefined')

        if (policiesResponse.return && Array.isArray(policiesResponse.return) && policiesResponse.return.length >= 2) {
          const [count, firstPolicyId] = policiesResponse.return
          console.log(`Found ${count} policies for owner, starting from ID ${firstPolicyId}`)
          console.log('Count type:', typeof count, 'FirstPolicyId type:', typeof firstPolicyId)
          
          const policiesList: Policy[] = []

          // Fetch each policy's details
          for (let i = 0; i < Number(count); i++) {
            try {
              const policyId = Number(firstPolicyId) + i
              console.log(`Fetching policy ${policyId}...`)
              
              const policyResponse = await appClient.send.getPolicy({
                args: [BigInt(policyId)]
              })
              console.log(`Policy ${policyId} response:`, policyResponse)
              console.log(`Policy ${policyId} return:`, policyResponse.return)
              console.log(`Policy ${policyId} return type:`, typeof policyResponse.return)
              console.log(`Policy ${policyId} return is array:`, Array.isArray(policyResponse.return))

              if (policyResponse.return) {
                // Handle both array and object formats
                let policyData: any
                
                if (Array.isArray(policyResponse.return)) {
                  // Array format: [owner, zipCode, t0, t1, cap, direction, threshold, slope, feePaid, settled]
                  const [owner, zipCode, t0, t1, cap, direction, threshold, slope, feePaid, settled] = policyResponse.return
                  policyData = { owner, zipCode, t0, t1, cap, direction, threshold, slope, feePaid, settled }
                } else if (typeof policyResponse.return === 'object') {
                  // Object format: {owner: "...", zipCode: "...", t0: 1758153600n, ...}
                  policyData = policyResponse.return
                } else {
                  console.log(`Policy ${policyId} returned invalid format:`, policyResponse.return)
                  continue
                }
                
                console.log(`Policy ${policyId} data:`, policyData)
                
                // Extract values from the policy data
                const { owner, zipCode, t0, t1, cap, direction, threshold, slope, feePaid, settled } = policyData
                
                // Convert Unix timestamps to dates
                const startDate = new Date(Number(t0) * 1000).toISOString().split('T')[0]
                const endDate = new Date(Number(t1) * 1000).toISOString().split('T')[0]
                
                // Convert microALGOs to ALGO
                const coverageAmount = (Number(cap) / 1000000).toFixed(2)
                const fee = (Number(feePaid) / 1000000).toFixed(2)

                const processedPolicy = {
                  id: policyId,
                  zipCode: typeof zipCode === 'string' ? zipCode : new TextDecoder().decode(zipCode),
                  startDate,
                  endDate,
                  coverageAmount,
                  fee,
                  status: (settled ? 'settled' : (new Date() > new Date(endDate) ? 'expired' : 'active')) as Policy['status'],
                  settled: Boolean(settled),
                  owner: owner,
                  direction: Number(direction),
                  threshold: Number(threshold),
                  slope: Number(slope),
                  feePaid: Number(feePaid)
                }
                
                console.log(`Policy ${policyId} processed data:`, processedPolicy)
                policiesList.push(processedPolicy)
              } else {
                console.log(`Policy ${policyId} returned no data:`, policyResponse.return)
              }
            } catch (error) {
              console.error(`Error fetching policy ${Number(firstPolicyId) + i}:`, error)
            }
          }

          console.log('Final policies list:', policiesList)
          setPolicies(policiesList)
          enqueueSnackbar(`Found ${policiesList.length} policies`, { variant: 'success' })
        } else {
          console.log('No policies found for this owner or invalid response format')
          console.log('Response details:', {
            hasReturn: !!policiesResponse.return,
            isArray: Array.isArray(policiesResponse.return),
            length: policiesResponse.return ? policiesResponse.return.length : 'undefined',
            returnValue: policiesResponse.return
          })
          setPolicies([])
        }
      } catch (error) {
        console.error('Error testing contract methods:', error)
        enqueueSnackbar(`Error testing contract: ${error}`, { variant: 'error' })
      }
    } catch (error: any) {
      enqueueSnackbar(`Error fetching policies: ${error.message}`, { variant: 'error' })
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (activeAddress) {
      fetchPolicies()
    }
  }, [activeAddress])

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'success'
      case 'settled': return 'info'
      case 'expired': return 'default'
      default: return 'default'
    }
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString()
  }

  const fileClaim = async (policy: Policy) => {
    if (!activeAddress) {
      enqueueSnackbar('Please connect your wallet first', { variant: 'error' })
      return
    }

    setClaimingPolicies(prev => new Set(prev).add(policy.id))

    try {
      const claimData = {
        policy_id: policy.id,
        zip_code: policy.zipCode,
        start_date: policy.startDate,
        end_date: policy.endDate,
        coverage_amount: policy.coverageAmount,
        direction: policy.direction,
        threshold: policy.threshold,
        slope: policy.slope,
        fee_paid: policy.feePaid,
        settled: policy.settled,
        owner: policy.owner
      }

      console.log('Filing claim for policy:', policy.id, claimData)

      const response = await fetch('http://localhost:8000/oracle-settle', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(claimData)
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const result: ClaimResult = await response.json()
      console.log('Claim result:', result)

      setClaimResults(prev => new Map(prev).set(policy.id, result))

      if (result.decision === 1) {
        enqueueSnackbar(`Claim approved! ${result.settlement_amount / 1_000_000} ALGO payout`, { variant: 'success' })
      } else {
        enqueueSnackbar('Claim rejected', { variant: 'info' })
      }

      // Auto-expand the claim result
      setExpandedClaims(prev => new Set(prev).add(policy.id))

    } catch (error: any) {
      console.error('Error filing claim:', error)
      enqueueSnackbar(`Error filing claim: ${error.message}`, { variant: 'error' })

      // Add error result
      const errorResult: ClaimResult = {
        decision: -1,
        reasoning: 'Error processing claim',
        reasoning_steps: [`Error: ${error.message}`],
        web_sources: [],
        confidence: 0,
        settlement_amount: 0,
        transaction_success: false
      }
      setClaimResults(prev => new Map(prev).set(policy.id, errorResult))
      setExpandedClaims(prev => new Set(prev).add(policy.id))
    } finally {
      setClaimingPolicies(prev => {
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

  return (
    <Box>
      <Box sx={{
        textAlign: 'center',
        mb: 4,
        background: 'linear-gradient(135deg, rgba(25, 118, 210, 0.1), rgba(21, 101, 192, 0.1))',
        borderRadius: 3,
        p: 3,
        border: '1px solid rgba(25, 118, 210, 0.2)'
      }}>
        <Typography
          variant="h3"
          gutterBottom
          sx={{
            fontWeight: 700,
            background: 'linear-gradient(45deg, #1976d2, #1565c0)',
            backgroundClip: 'text',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            mb: 1
          }}
        >
          Claims
        </Typography>
        <Typography variant="h6" sx={{ color: 'text.secondary', fontWeight: 400 }}>
          View your policies and settle claims with AI-powered decision making
        </Typography>
      </Box>

      {!activeAddress ? (
        <Alert
          severity="warning"
          sx={{
            mb: 3,
            borderRadius: 2,
            backgroundColor: 'rgba(251, 191, 36, 0.1)',
            border: '1px solid rgba(251, 191, 36, 0.3)'
          }}
        >
          Please connect your wallet to view your policies
        </Alert>
      ) : loading ? (
        <Box sx={{
          backgroundColor: 'rgba(255, 255, 255, 0.9)',
          borderRadius: 4,
          p: 5,
          border: '1px solid rgba(255, 255, 255, 0.4)',
          backdropFilter: 'blur(20px)',
          boxShadow: '0 15px 50px rgba(0, 0, 0, 0.12), 0 0 30px rgba(25, 118, 210, 0.08), inset 0 1px 0 rgba(255, 255, 255, 0.6)',
          textAlign: 'center',
          position: 'relative',
          transition: 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
          '&:hover': {
            transform: 'translateY(-1px)',
            boxShadow: '0 18px 55px rgba(0, 0, 0, 0.14), 0 0 35px rgba(25, 118, 210, 0.1), inset 0 1px 0 rgba(255, 255, 255, 0.7)',
          },
          '&::before': {
            content: '""',
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            height: '1px',
            background: 'linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.8), transparent)',
            borderRadius: '4px 4px 0 0',
          },
        }}>
          <CircularProgress sx={{ mb: 2 }} />
          <Typography variant="body1">
            Loading your policies...
          </Typography>
        </Box>
      ) : policies.length === 0 ? (
        <Box sx={{
          backgroundColor: 'rgba(255, 255, 255, 0.9)',
          borderRadius: 4,
          p: 7,
          border: '1px solid rgba(255, 255, 255, 0.4)',
          backdropFilter: 'blur(20px)',
          boxShadow: '0 15px 50px rgba(0, 0, 0, 0.12), 0 0 30px rgba(25, 118, 210, 0.08), inset 0 1px 0 rgba(255, 255, 255, 0.6)',
          textAlign: 'center',
          position: 'relative',
          transition: 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
          '&:hover': {
            transform: 'translateY(-1px)',
            boxShadow: '0 18px 55px rgba(0, 0, 0, 0.14), 0 0 35px rgba(25, 118, 210, 0.1), inset 0 1px 0 rgba(255, 255, 255, 0.7)',
          },
          '&::before': {
            content: '""',
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            height: '1px',
            background: 'linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.8), transparent)',
            borderRadius: '4px 4px 0 0',
          },
        }}>
          <Typography variant="h6" sx={{ color: 'text.secondary', mb: 2 }}>
            No policies found
          </Typography>
          <Typography variant="body1" sx={{ color: 'text.secondary', mb: 3 }}>
            Purchase a policy in the Guard tab to see it here
          </Typography>
          <Typography variant="body2" sx={{ color: 'text.secondary' }}>
            Check the browser console for debugging information
          </Typography>
        </Box>
      ) : (
        <>
          <Box sx={{ display: 'flex', justifyContent: 'flex-end', mb: 2 }}>
            <Button
              variant="outlined"
              onClick={fetchPolicies}
              disabled={loading}
              startIcon={loading ? <CircularProgress size={20} /> : null}
              sx={{
                borderRadius: 3,
                borderColor: '#1976d2',
                color: '#1976d2',
                fontWeight: 600,
                '&:hover': {
                  borderColor: '#1565c0',
                  backgroundColor: 'rgba(25, 118, 210, 0.1)',
                },
                px: 3,
                py: 1
              }}
            >
              {loading ? 'Refreshing...' : 'Refresh'}
            </Button>
          </Box>

          <Box sx={{
            backgroundColor: 'rgba(255, 255, 255, 0.9)',
            borderRadius: 4,
            border: '1px solid rgba(255, 255, 255, 0.4)',
            backdropFilter: 'blur(20px)',
            boxShadow: '0 15px 50px rgba(0, 0, 0, 0.12), 0 0 30px rgba(25, 118, 210, 0.08), inset 0 1px 0 rgba(255, 255, 255, 0.6)',
            overflow: 'hidden',
            position: 'relative',
            transition: 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
            '&:hover': {
              transform: 'translateY(-1px)',
              boxShadow: '0 18px 55px rgba(0, 0, 0, 0.14), 0 0 35px rgba(25, 118, 210, 0.1), inset 0 1px 0 rgba(255, 255, 255, 0.7)',
            },
            '&::before': {
              content: '""',
              position: 'absolute',
              top: 0,
              left: 0,
              right: 0,
              height: '1px',
              background: 'linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.8), transparent)',
              borderRadius: '4px 4px 0 0',
            },
          }}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Policy ID</TableCell>
                <TableCell>ZIP Code</TableCell>
                <TableCell>Coverage Period</TableCell>
                <TableCell>Coverage Amount</TableCell>
                <TableCell>Fee Paid</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Parameters</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {policies.map((policy) => (
                <TableRow key={policy.id}>
                  <TableCell>{policy.id}</TableCell>
                  <TableCell>{policy.zipCode}</TableCell>
                  <TableCell>
                    {formatDate(policy.startDate)} - {formatDate(policy.endDate)}
                  </TableCell>
                  <TableCell>{policy.coverageAmount} ALGO</TableCell>
                  <TableCell>{policy.fee} ALGO</TableCell>
                  <TableCell>
                    <Chip 
                      label={policy.status.toUpperCase()} 
                      color={getStatusColor(policy.status) as any}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    <Typography variant="caption" display="block">
                      Direction: {policy.direction === 1 ? 'Below' : 'Above'} threshold
                    </Typography>
                    <Typography variant="caption" display="block">
                      Threshold: {policy.threshold}
                    </Typography>
                    <Typography variant="caption" display="block">
                      Slope: {policy.slope}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    {policy.status === 'active' && (
                      <Button
                        variant="contained"
                        size="small"
                        onClick={() => fileClaim(policy)}
                        disabled={claimingPolicies.has(policy.id)}
                        startIcon={claimingPolicies.has(policy.id) ? <CircularProgress size={16} /> : null}
                        sx={{
                          backgroundColor: '#1976d2',
                          '&:hover': {
                            backgroundColor: '#1565c0',
                          },
                          fontSize: '0.75rem',
                          px: 2,
                          py: 0.5
                        }}
                      >
                        {claimingPolicies.has(policy.id) ? 'Processing...' : 'File Claim'}
                      </Button>
                    )}
                    {policy.status === 'settled' && claimResults.has(policy.id) && (
                      <Button
                        variant="outlined"
                        size="small"
                        onClick={() => toggleClaimExpansion(policy.id)}
                        endIcon={expandedClaims.has(policy.id) ? <ExpandLessIcon /> : <ExpandMoreIcon />}
                        sx={{
                          borderColor: '#1976d2',
                          color: '#1976d2',
                          fontSize: '0.75rem',
                          px: 2,
                          py: 0.5
                        }}
                      >
                        {expandedClaims.has(policy.id) ? 'Hide' : 'View'} Result
                      </Button>
                    )}
                  </TableCell>
                </TableRow>
              ))}

              {/* Claim Results Rows */}
              {policies.map((policy) => (
                claimResults.has(policy.id) && (
                  <TableRow key={`claim-${policy.id}`}>
                    <TableCell colSpan={8} sx={{ padding: 0, borderBottom: 'none' }}>
                      <Collapse in={expandedClaims.has(policy.id)}>
                        <Box sx={{
                          p: 3,
                          backgroundColor: 'rgba(0, 0, 0, 0.02)',
                          border: '1px solid rgba(0, 0, 0, 0.08)',
                          borderRadius: 1,
                          mt: 1,
                          mb: 2
                        }}>
                          {(() => {
                            const result = claimResults.get(policy.id)!
                            const isApproved = result.decision === 1
                            const isError = result.decision === -1

                            return (
                              <Box>
                                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                                  <Typography variant="h6" sx={{
                                    fontWeight: 600,
                                    color: isError ? '#d32f2f' : isApproved ? '#2e7d32' : '#f57c00'
                                  }}>
                                    {isError ? 'Claim Error' : isApproved ? 'Claim Approved' : 'Claim Rejected'}
                                  </Typography>
                                  <Chip
                                    label={`${(result.confidence * 100).toFixed(1)}% Confidence`}
                                    size="small"
                                    color={isApproved ? 'success' : 'default'}
                                  />
                                </Box>

                                {!isError && (
                                  <Box sx={{ mb: 3 }}>
                                    <Typography variant="body1" sx={{ fontWeight: 500, mb: 2 }}>
                                      {result.reasoning}
                                    </Typography>

                                    {result.settlement_amount > 0 && (
                                      <Alert severity="success" sx={{ mb: 2 }}>
                                        <strong>Payout Amount:</strong> {(result.settlement_amount / 1_000_000).toFixed(6)} ALGO
                                      </Alert>
                                    )}
                                  </Box>
                                )}

                                <Typography variant="h6" sx={{ fontWeight: 600, color: '#1976d2', mb: 2 }}>
                                  Decision Process:
                                </Typography>
                                {result.reasoning_steps.map((step, index) => (
                                  <Box key={index} sx={{ mb: 2, display: 'flex', gap: 2 }}>
                                    <Box sx={{
                                      minWidth: 24,
                                      height: 24,
                                      borderRadius: '50%',
                                      backgroundColor: '#1976d2',
                                      color: 'white',
                                      display: 'flex',
                                      alignItems: 'center',
                                      justifyContent: 'center',
                                      fontSize: '0.875rem',
                                      fontWeight: 600,
                                      flexShrink: 0
                                    }}>
                                      {index + 1}
                                    </Box>
                                    <Typography variant="body2" sx={{ lineHeight: 1.5, pt: 0.5 }}>
                                      {step}
                                    </Typography>
                                  </Box>
                                ))}

                                {result.transaction_success && result.transaction_id && (
                                  <Alert severity="info" sx={{ mt: 2 }}>
                                    <strong>Transaction ID:</strong> {result.transaction_id}
                                  </Alert>
                                )}
                              </Box>
                            )
                          })()}
                        </Box>
                      </Collapse>
                    </TableCell>
                  </TableRow>
                )
              ))}
            </TableBody>
          </Table>
        </Box>
        </>
      )}
    </Box>
  )
}

export default ClaimTab
