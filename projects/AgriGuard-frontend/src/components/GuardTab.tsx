import React, { useState } from 'react'
import {
  Box,
  Card,
  CardContent,
  TextField,
  Button,
  Typography,
  Grid,
  Alert,
  CircularProgress,
  Stepper,
  Step,
  StepLabel,
  Divider,
  IconButton,
  Tooltip,
  Paper
} from '@mui/material'
import InfoIcon from '@mui/icons-material/Info'
import { styled } from '@mui/material/styles'
import { useWallet } from '@txnlab/use-wallet-react'
import { useSnackbar } from 'notistack'
import { AgriGuardInsuranceFactory } from '../contracts/AgriGuardInsurance'
import { getAlgodConfigFromViteEnvironment, getIndexerConfigFromViteEnvironment } from '../utils/network/getAlgoClientConfigs'
import { AlgorandClient } from '@algorandfoundation/algokit-utils'
import { AlgoAmount } from '@algorandfoundation/algokit-utils/types/amount'
import { DEMO_MODE } from '../config/demo'
import { mockInsuranceClient } from '../mocks/MockInsuranceClient'
import { MOCK_WALLET_ADDRESS, formatAlgo } from '../mocks/mockData'

// Minimalistic styled components
const MinimalCard = styled(Card)({
  backgroundColor: '#ffffff',
  borderRadius: 8,
  border: '1px solid #f0f0f0',
  boxShadow: 'none',
})

const MinimalTextField = styled(TextField)({
  '& .MuiOutlinedInput-root': {
    borderRadius: 6,
    '& fieldset': {
      borderColor: '#e0e0e0',
    },
    '&:hover fieldset': {
      borderColor: '#b0b0b0',
    },
    '&.Mui-focused fieldset': {
      borderColor: '#000000',
    },
  },
})

const MinimalButton = styled(Button)({
  borderRadius: 6,
  textTransform: 'none',
  fontWeight: 500,
  fontSize: '0.875rem',
  padding: '10px 24px',
})

const MinimalStepper = styled(Stepper)({
  '& .MuiStepLabel-root': {
    '& .MuiStepLabel-label': {
      fontSize: '0.875rem',
      fontWeight: 500,
    },
  },
  '& .MuiStepConnector-root': {
    '& .MuiStepConnector-line': {
      borderColor: '#e0e0e0',
      borderTopWidth: 2,
    },
  },
  '& .MuiStepConnector-active .MuiStepConnector-line': {
    borderColor: '#000000',
  },
  '& .MuiStepConnector-completed .MuiStepConnector-line': {
    borderColor: '#000000',
  },
})

const MinimalStepIcon = styled(Box)<{ active?: boolean; completed?: boolean }>(({ active, completed }) => ({
  width: 24,
  height: 24,
  borderRadius: '50%',
  backgroundColor: completed ? '#000000' : active ? '#000000' : '#e0e0e0',
  color: completed || active ? '#ffffff' : '#666666',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  fontSize: '0.75rem',
  fontWeight: 600,
}))

interface RiskAnalysis {
  risk_score: number
  uncertainty: number
  direction: number
  threshold: string
  slope: string
  fee: string
  reasoning: string
  reasoning_steps: string[]
  web_sources: string[]
  confidence: number
  analysis_summary: string
  threshold_numeric: number
  slope_numeric: number
  coverage_amount: number
}

const GuardTab: React.FC = () => {
  const { activeAddress, transactionSigner } = useWallet()
  const { enqueueSnackbar } = useSnackbar()
  
  const [formData, setFormData] = useState({
    zipCode: '',
    startDate: '',
    endDate: '',
    coverageAmount: '',
    description: ''
  })
  
  const [currentStep, setCurrentStep] = useState(0)
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [isPurchasing, setIsPurchasing] = useState(false)
  const [riskAnalysis, setRiskAnalysis] = useState<RiskAnalysis | null>(null)
  const [showReasoning, setShowReasoning] = useState(false)

  const steps = ['Enter Information', 'AI Analysis', 'Purchase Policy']

  const handleInputChange = (field: string) => (event: React.ChangeEvent<HTMLInputElement>) => {
    setFormData(prev => ({
      ...prev,
      [field]: event.target.value
    }))
  }

  const isFormValid = () => {
    return formData.zipCode && formData.startDate && formData.endDate && 
           formData.coverageAmount && formData.description
  }

  const handleAnalyze = async () => {
    if (!isFormValid()) {
      enqueueSnackbar('Please fill in all required fields', { variant: 'error' })
      return
    }

    setIsAnalyzing(true)
    setCurrentStep(1)

    try {
      const response = await fetch('http://localhost:8000/analyze-risk', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          description: formData.description,
          zipCode: formData.zipCode,
          startTime: formData.startDate,
          endTime: formData.endDate,
          cap: formData.coverageAmount
        }),
      })

      if (!response.ok) {
        throw new Error('Analysis failed')
      }

      const data = await response.json()
      setRiskAnalysis(data)
      setCurrentStep(2)
    } catch (error) {
      console.error('Analysis error:', error)
      enqueueSnackbar('Analysis failed. Please try again.', { variant: 'error' })
      setCurrentStep(0)
    } finally {
      setIsAnalyzing(false)
    }
  }

  const handlePurchase = async () => {
    if (!activeAddress || !transactionSigner || !riskAnalysis) {
      enqueueSnackbar('Please connect your wallet', { variant: 'error' })
      return
    }

    setIsPurchasing(true)

    try {
      const algodConfig = getAlgodConfigFromViteEnvironment()
      const indexerConfig = getIndexerConfigFromViteEnvironment()
      
      const algorand = AlgorandClient.fromConfig({ algodConfig })

      // Set the default signer for the algorand client
      if (transactionSigner) {
        algorand.setDefaultSigner(transactionSigner)
      }

      const appFactory = new AgriGuardInsuranceFactory({
        defaultSender: activeAddress ?? undefined,
        algorand,
      })

      const appClient = appFactory.getAppClientById({
        appId: BigInt(import.meta.env.VITE_APP_ID || '1061'),
      })

      const startTimestamp = Math.floor(new Date(formData.startDate).getTime() / 1000)
      const endTimestamp = Math.floor(new Date(formData.endDate).getTime() / 1000)
      const coverageAmountMicroAlgo = AlgoAmount.Algos(parseFloat(formData.coverageAmount)).microAlgos
      const feeMicroAlgo = Number(riskAnalysis.fee) * 1000000

      // First, send payment to the contract address
      const contractAddress = import.meta.env.VITE_APP_ADDRESS
      if (!contractAddress) {
        throw new Error('Contract address not configured')
      }

      // Create and send payment transaction using AlgoKit Utils
      const paymentResult = await algorand.send.payment({
        sender: activeAddress,
        receiver: contractAddress,
        amount: AlgoAmount.MicroAlgo(feeMicroAlgo),
        note: new TextEncoder().encode('Policy payment')
      })
      console.log('Payment transaction:', paymentResult)

      // Then call buyPolicy method
      const result = await appClient.send.buyPolicy({
        args: [
          new TextEncoder().encode(formData.zipCode), // zip_code
          BigInt(startTimestamp), // t0
          BigInt(endTimestamp), // t1
          BigInt(coverageAmountMicroAlgo), // cap
          BigInt(0), // direction
          BigInt(riskAnalysis.threshold_numeric), // threshold (numeric)
          BigInt(riskAnalysis.slope_numeric), // slope (numeric)
          BigInt(feeMicroAlgo) // fee
        ]
      })

      if (result.return) {
        const policyId = result.return
        enqueueSnackbar(`Policy purchased successfully! Policy ID: ${policyId}`, { variant: 'success' })
      } else {
        enqueueSnackbar('Policy purchased successfully!', { variant: 'success' })
      }
      
      // Reset form
      setFormData({
        zipCode: '',
        startDate: '',
        endDate: '',
        coverageAmount: '',
        description: ''
      })
      setRiskAnalysis(null)
      setCurrentStep(0)
    } catch (error: any) {
      console.error('Purchase error:', error)
      enqueueSnackbar(`Purchase failed: ${error.message}`, { variant: 'error' })
    } finally {
      setIsPurchasing(false)
    }
  }

  const handleReset = () => {
      setFormData({
        zipCode: '',
        startDate: '',
        endDate: '',
        coverageAmount: '',
        description: ''
      })
    setRiskAnalysis(null)
    setCurrentStep(0)
  }

  const CustomStepIcon = (props: any) => {
    const { active, completed, icon } = props
    return (
      <MinimalStepIcon active={active} completed={completed}>
        {completed ? '✓' : icon}
      </MinimalStepIcon>
    )
  }

  return (
    <Box sx={{ maxWidth: 800, mx: 'auto', p: 3 }}>
      <Typography variant="h4" sx={{ mb: 4, fontWeight: 300, textAlign: 'center' }}>
        Agricultural Insurance Policy
      </Typography>

      <MinimalStepper activeStep={currentStep} alternativeLabel sx={{ mb: 4 }}>
        {steps.map((label, index) => (
          <Step key={label}>
            <StepLabel StepIconComponent={CustomStepIcon}>{label}</StepLabel>
          </Step>
        ))}
      </MinimalStepper>

      {currentStep === 0 && (
        <MinimalCard>
          <CardContent sx={{ p: 4 }}>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
              <Box sx={{ display: 'flex', gap: 3, flexWrap: 'wrap' }}>
                <Box sx={{ flex: 1, minWidth: '200px' }}>
                  <MinimalTextField
                    fullWidth
                    label="ZIP Code"
                    value={formData.zipCode}
                    onChange={handleInputChange('zipCode')}
                    placeholder="Enter ZIP code"
                  />
                </Box>
                <Box sx={{ flex: 1, minWidth: '200px' }}>
                  <MinimalTextField
                    fullWidth
                    label="Coverage Amount (ALGO)"
                    type="number"
                    value={formData.coverageAmount}
                    onChange={handleInputChange('coverageAmount')}
                    placeholder="Enter coverage amount"
                  />
                </Box>
              </Box>
              <Box sx={{ display: 'flex', gap: 3, flexWrap: 'wrap' }}>
                <Box sx={{ flex: 1, minWidth: '200px' }}>
                  <MinimalTextField
                    fullWidth
                    label="Start Date"
                    type="date"
                    value={formData.startDate}
                    onChange={handleInputChange('startDate')}
                    InputLabelProps={{ shrink: true }}
                  />
                </Box>
                <Box sx={{ flex: 1, minWidth: '200px' }}>
                  <MinimalTextField
                    fullWidth
                    label="End Date"
                    type="date"
                    value={formData.endDate}
                    onChange={handleInputChange('endDate')}
                    InputLabelProps={{ shrink: true }}
                  />
                </Box>
              </Box>
              <Box>
                <MinimalTextField
                  fullWidth
                  label="Description"
                  multiline
                  rows={3}
                  value={formData.description}
                  onChange={handleInputChange('description')}
                  placeholder="Describe your agricultural operation, crops, and risk factors..."
                />
              </Box>
            </Box>

            <Box sx={{ mt: 4, display: 'flex', justifyContent: 'center' }}>
              <MinimalButton
                variant="contained"
                onClick={handleAnalyze}
                disabled={!isFormValid()}
                sx={{
                  backgroundColor: '#000000',
                  color: '#ffffff',
                  '&:hover': {
                    backgroundColor: '#333333',
                  },
                }}
              >
                Analyze Risk
              </MinimalButton>
            </Box>
          </CardContent>
        </MinimalCard>
      )}

      {currentStep === 1 && (
        <MinimalCard>
          <CardContent sx={{ p: 4, textAlign: 'center' }}>
            <CircularProgress sx={{ mb: 2 }} />
            <Typography variant="h6" sx={{ mb: 1 }}>
              Analyzing Risk...
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Please wait while we analyze your agricultural risk factors.
            </Typography>
          </CardContent>
        </MinimalCard>
      )}

      {currentStep === 2 && riskAnalysis && (
        <MinimalCard>
          <CardContent sx={{ p: 4 }}>
            <Typography variant="h5" sx={{ mb: 3, fontWeight: 400 }}>
              Risk Analysis Results
            </Typography>

            <Box sx={{ display: 'flex', gap: 3, mb: 3, flexWrap: 'wrap' }}>
              <Box sx={{ flex: 1, minWidth: '200px' }}>
                <Paper sx={{ p: 2, textAlign: 'center', border: '1px solid #f0f0f0' }}>
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                    Risk Score
                  </Typography>
                  <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 1 }}>
                    <Typography variant="h4" sx={{ fontWeight: 300 }}>
                      {riskAnalysis.risk_score}%
                    </Typography>
                    <Tooltip 
                      title={
                        <Box>
                          <Typography variant="subtitle2" sx={{ mb: 1, fontWeight: 600 }}>
                            AI Analysis Steps:
                          </Typography>
                          {riskAnalysis.reasoning_steps.map((step, index) => (
                            <Typography key={index} variant="body2" sx={{ mb: 0.5 }}>
                              {step}
                            </Typography>
                          ))}
                        </Box>
                      } 
                      arrow
                      placement="top"
                    >
                      <IconButton
                        size="small"
                        onMouseEnter={() => setShowReasoning(true)}
                        onMouseLeave={() => setShowReasoning(false)}
                      >
                        <InfoIcon fontSize="small" />
                      </IconButton>
                    </Tooltip>
                  </Box>
                </Paper>
              </Box>
              <Box sx={{ flex: 1, minWidth: '200px' }}>
                <Paper sx={{ p: 2, textAlign: 'center', border: '1px solid #f0f0f0' }}>
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                    Premium Fee
                  </Typography>
                  <Typography variant="h4" sx={{ fontWeight: 300 }}>
                    {Number(riskAnalysis.fee).toFixed(2)} ALGO
                  </Typography>
                </Paper>
              </Box>
              <Box sx={{ flex: 1, minWidth: '200px' }}>
                <Paper sx={{ p: 2, textAlign: 'center', border: '1px solid #f0f0f0' }}>
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                    Coverage Amount
                  </Typography>
                  <Typography variant="h4" sx={{ fontWeight: 300 }}>
                    {Number(formData.coverageAmount).toFixed(2)} ALGO
                  </Typography>
                </Paper>
              </Box>
            </Box>

            <Divider sx={{ my: 3 }} />

            <Box sx={{ mb: 3 }}>
              <Typography variant="h6" sx={{ mb: 2, fontWeight: 500 }}>
                Analysis Summary
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                {riskAnalysis.analysis_summary}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Confidence: {(riskAnalysis.confidence * 100).toFixed(1)}%
              </Typography>
            </Box>

            <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center' }}>
              <MinimalButton
                variant="outlined"
                onClick={handleReset}
                sx={{
                  borderColor: '#e0e0e0',
                  color: '#666666',
                  '&:hover': {
                    borderColor: '#b0b0b0',
                    backgroundColor: '#f5f5f5',
                  },
                }}
              >
                Start Over
              </MinimalButton>
              <MinimalButton
                variant="contained"
                onClick={handlePurchase}
                disabled={isPurchasing}
                sx={{
                  backgroundColor: '#000000',
                  color: '#ffffff',
                  '&:hover': {
                    backgroundColor: '#333333',
                  },
                  '&:disabled': {
                    backgroundColor: '#e0e0e0',
                    color: '#999999',
                  },
                }}
              >
                {isPurchasing ? 'Purchasing...' : 'Purchase Policy'}
              </MinimalButton>
            </Box>
          </CardContent>
        </MinimalCard>
      )}
    </Box>
  )
}

export default GuardTab