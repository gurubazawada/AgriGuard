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
  Divider,
  Stepper,
  Step,
  StepLabel,
  StepConnector,
  stepConnectorClasses,
  IconButton
} from '@mui/material'
import InfoIcon from '@mui/icons-material/Info'
import { styled } from '@mui/material/styles'
import { useWallet } from '@txnlab/use-wallet-react'
import { useSnackbar } from 'notistack'
import { AgriGuardInsuranceFactory } from '../contracts/AgriGuardInsurance'
import { getAlgodConfigFromViteEnvironment, getIndexerConfigFromViteEnvironment } from '../utils/network/getAlgoClientConfigs'
import { AlgorandClient } from '@algorandfoundation/algokit-utils'
import { AlgoAmount } from '@algorandfoundation/algokit-utils/types/amount'

// Custom Stepper Components
const CustomStepConnector = styled(StepConnector)(({ theme }) => ({
  [`&.${stepConnectorClasses.alternativeLabel}`]: {
    top: 22,
  },
  [`&.${stepConnectorClasses.active}`]: {
    [`& .${stepConnectorClasses.line}`]: {
      background: '#1976d2',
    },
  },
  [`&.${stepConnectorClasses.completed}`]: {
    [`& .${stepConnectorClasses.line}`]: {
      background: '#1976d2',
    },
  },
  [`& .${stepConnectorClasses.line}`]: {
    height: 3,
    border: 0,
    backgroundColor: '#eaeaf0',
    borderRadius: 1,
  },
}))

const CustomStepIconRoot = styled('div')<{
  ownerState: { completed?: boolean; active?: boolean; icon?: number }
}>(({ theme, ownerState }) => ({
  backgroundColor: '#ccc',
  zIndex: 1,
  color: '#fff',
  width: 40,
  height: 40,
  display: 'flex',
  borderRadius: '50%',
  justifyContent: 'center',
  alignItems: 'center',
  fontSize: '1rem',
  fontWeight: 'bold',
  transition: 'all 0.3s ease',
  ...(ownerState.active && {
    background: '#1976d2',
    boxShadow: '0 4px 20px rgba(25, 118, 210, 0.4)',
    transform: 'scale(1.05)',
  }),
  ...(ownerState.completed && {
    background: '#1976d2',
    boxShadow: '0 4px 20px rgba(25, 118, 210, 0.3)',
  }),
}))

function CustomStepIcon(props: any) {
  const { active, completed, className, icon } = props

  const icons: { [index: string]: string } = {
    1: '',
    2: '',
    3: '',
  }

  return (
    <CustomStepIconRoot ownerState={{ completed, active, icon: Number(icon) }} className={className}>
      {icons[String(icon)]}
    </CustomStepIconRoot>
  )
}

interface PolicyFormData {
  zipCode: string
  startDate: string
  endDate: string
  coverageAmount: string
  description: string
}

interface RiskAnalysis {
  riskScore: number
  uncertainty: number
  direction: number
  threshold: string
  slope: string
  fee: string
  reasoning: string[]
  confidence: number
  thresholdNumeric: number
  slopeNumeric: number
  feeMicroAlgo: number
  coverage?: string
  recommendations?: string
}

const GuardTab: React.FC = () => {
  const { activeAddress, transactionSigner } = useWallet()
  const { enqueueSnackbar } = useSnackbar()
  const [loading, setLoading] = useState(false)
  const [analyzing, setAnalyzing] = useState(false)
  const [activeStep, setActiveStep] = useState(-1)
  const [formData, setFormData] = useState<PolicyFormData>({
    zipCode: '',
    startDate: '',
    endDate: '',
    coverageAmount: '',
    description: ''
  })
  const [riskAnalysis, setRiskAnalysis] = useState<RiskAnalysis | null>(null)
  const [policies, setPolicies] = useState<any[]>([])

  const steps = [
    'Enter Information',
    'AI Risk Analysis',
    'Purchase Policy'
  ]

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

  const handleInputChange = (field: keyof PolicyFormData) => (event: React.ChangeEvent<HTMLInputElement>) => {
    setFormData(prev => ({
      ...prev,
      [field]: event.target.value
    }))
  }

  const analyzeRisk = async () => {
    if (!formData.zipCode || !formData.startDate || !formData.endDate || !formData.coverageAmount || !formData.description) {
      enqueueSnackbar('Please fill in all fields', { variant: 'error' })
      return
    }

    // Move to step 1 (actively working on information entry)
    setActiveStep(0)
    setAnalyzing(true)
    try {
      const response = await fetch('http://localhost:8000/analyze-risk', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          zipCode: formData.zipCode,
          startTime: formData.startDate,
          endTime: formData.endDate,
          cap: formData.coverageAmount,
          description: formData.description
        })
      })

      if (!response.ok) {
        throw new Error('Failed to analyze risk')
      }

      const analysis = await response.json()
      setRiskAnalysis({
        riskScore: analysis.risk_score,
        uncertainty: analysis.uncertainty,
        direction: analysis.direction,
        threshold: analysis.threshold,
        slope: analysis.slope,
        fee: analysis.fee,
        reasoning: analysis.reasoning_steps || [],
        confidence: analysis.confidence || 0,
        // Store numeric values for smart contract
        thresholdNumeric: analysis.threshold_numeric,
        slopeNumeric: analysis.slope_numeric,
        feeMicroAlgo: analysis.fee_micro_algo
      })

      // Move to step 2 (AI Risk Analysis completed)
      setActiveStep(1)

      enqueueSnackbar('Risk analysis completed!', { variant: 'success' })
    } catch (error: any) {
      enqueueSnackbar(`Error analyzing risk: ${error.message}`, { variant: 'error' })
    } finally {
      setAnalyzing(false)
    }
  }

  const buyPolicy = async () => {
    if (!riskAnalysis || !activeAddress || !transactionSigner) {
      enqueueSnackbar('Please complete risk analysis and connect wallet', { variant: 'error' })
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

      // Convert dates to Unix timestamps
      const startTime = Math.floor(new Date(formData.startDate).getTime() / 1000)
      const endTime = Math.floor(new Date(formData.endDate).getTime() / 1000)
      
      // Convert coverage amount to microALGOs
      const coverageMicroAlgo = Math.floor(parseFloat(formData.coverageAmount) * 1000000)
      
      // Use the pre-calculated numeric values from the backend
      const feeMicroAlgo = Number(riskAnalysis.feeMicroAlgo) // Convert BigInt to number

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
      const response = await appClient.send.buyPolicy({
        args: [
          new TextEncoder().encode(formData.zipCode), // zip_code
          BigInt(startTime), // t0
          BigInt(endTime), // t1
          BigInt(coverageMicroAlgo), // cap
          BigInt(riskAnalysis.direction), // direction
          BigInt(riskAnalysis.thresholdNumeric), // threshold (numeric)
          BigInt(riskAnalysis.slopeNumeric), // slope (numeric)
          BigInt(feeMicroAlgo) // fee
        ]
      })

      if (response.return) {
        const policyId = response.return
        enqueueSnackbar(`Policy purchased successfully! Policy ID: ${policyId}`, { variant: 'success' })
        
        // Add to policies list
        setPolicies(prev => [...prev, {
          id: policyId,
          zipCode: formData.zipCode,
          startDate: formData.startDate,
          endDate: formData.endDate,
          coverageAmount: formData.coverageAmount,
          fee: riskAnalysis.fee,
          status: 'active'
        }])

        // Move to step 3 (Purchase Policy completed)
        setActiveStep(2)

        // Reset form after a short delay to show completion
        setTimeout(() => {
          setFormData({
            zipCode: '',
            startDate: '',
            endDate: '',
            coverageAmount: '',
            description: ''
          })
          setRiskAnalysis(null)
          setActiveStep(0) // Reset to step 1 for next policy
        }, 2000)
      }
    } catch (error: any) {
      enqueueSnackbar(`Error buying policy: ${error.message}`, { variant: 'error' })
    } finally {
      setLoading(false)
    }
  }

  return (
    <Box>
      {/* Progress Stepper */}
      <Box sx={{
        display: 'flex',
        justifyContent: 'center',
        mb: 3,
        mt: 1
      }}>
        <Box sx={{
          width: { xs: '85%', md: '60%' },
          maxWidth: 500
        }}>
          <Stepper activeStep={activeStep < 0 ? 0 : activeStep} alternativeLabel connector={<CustomStepConnector />}>
            {steps.map((label, index) => (
              <Step key={label}>
                <StepLabel StepIconComponent={CustomStepIcon}>
                  <Typography
                    variant="body2"
                    sx={{
                      fontWeight: (activeStep === index || (activeStep < 0 && index === 0)) ? 600 : activeStep > index ? 500 : 400,
                      color: (activeStep === index || (activeStep < 0 && index === 0)) ? '#1976d2' : activeStep > index ? '#1565c0' : 'text.secondary',
                      mt: 1
                    }}
                  >
                    {label}
                  </Typography>
                </StepLabel>
              </Step>
            ))}
          </Stepper>
        </Box>
      </Box>

      <Box sx={{
        textAlign: 'center',
        mb: 4,
        background: 'rgba(255, 255, 255, 0.8)',
        borderRadius: 8,
        p: 3,
        border: '1px solid rgba(0, 0, 0, 0.08)'
      }}>
        <Typography
          variant="h3"
          gutterBottom
          sx={{
            fontWeight: 600,
            color: '#1976d2',
            mb: 1
          }}
        >
          {activeStep === 0 && 'Step 1: Enter Information'}
          {activeStep === 1 && 'Step 2: AI Risk Analysis'}
          {activeStep === 2 && 'Step 3: Purchase Policy'}
          {activeStep === -1 && 'AgriGuard Insurance'}
        </Typography>
        <Typography variant="h6" sx={{ color: 'text.secondary', fontWeight: 400 }}>
          {activeStep === 0 && 'Fill out your policy details to get started'}
          {activeStep === 1 && 'AI is analyzing your risk parameters...'}
          {activeStep === 2 && 'Review and purchase your insurance policy'}
          {activeStep === -1 && 'Configure your insurance policy and get AI-powered risk assessment'}
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
          Please connect your wallet to purchase a policy
        </Alert>
      ) : null}

      {/* Policy Configuration Form - Center Third */}
      <Box sx={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'flex-start',
        minHeight: '60vh',
        py: 4
      }}>
        <Box sx={{
          width: { xs: '90%', md: '35%' },
          maxWidth: 480,
          backgroundColor: 'rgba(255, 255, 255, 0.95)',
          borderRadius: 8,
          p: 4,
          border: '1px solid rgba(0, 0, 0, 0.08)',
          backdropFilter: 'blur(15px)',
          boxShadow: '0 8px 32px rgba(0, 0, 0, 0.08), 0 4px 16px rgba(0, 0, 0, 0.04)',
          position: 'relative',
          transition: 'all 0.2s ease',
          '&:hover': {
            transform: 'translateY(-1px)',
            boxShadow: '0 12px 40px rgba(0, 0, 0, 0.1), 0 6px 20px rgba(0, 0, 0, 0.06)',
          },
        }}>
        <Typography
          variant="h5"
          gutterBottom
          sx={{
            mb: 3,
            fontWeight: 600,
            color: '#1976d2',
            textAlign: 'center',
          }}
        >
          {riskAnalysis ? 'AI Risk Analysis Results' : 'Policy Configuration'}
        </Typography>

          {riskAnalysis ? (
            // Risk Analysis Results
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
              {/* Risk Score Header */}
              <Box sx={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                p: 2,
                backgroundColor: 'rgba(25, 118, 210, 0.05)',
                borderRadius: 2,
                border: '1px solid rgba(25, 118, 210, 0.1)'
              }}>
                <Box>
                  <Typography variant="h6" sx={{ fontWeight: 600, color: '#1976d2', mb: 1 }}>
                    Risk Assessment Complete
                  </Typography>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                    <Typography variant="body1">
                      <strong>Risk Score:</strong>{' '}
                      <Box
                        component="span"
                        sx={{
                          color: riskAnalysis.riskScore > 70 ? '#d32f2f' : riskAnalysis.riskScore > 40 ? '#f57c00' : '#2e7d32',
                          fontWeight: 'bold',
                          fontSize: '1.1em',
                          display: 'inline-flex',
                          alignItems: 'center',
                          gap: 0.5
                        }}
                      >
                        {riskAnalysis.riskScore}/100
                        <IconButton
                          size="small"
                          sx={{
                            color: 'inherit',
                            p: 0.5,
                            '&:hover': {
                              backgroundColor: 'rgba(255, 255, 255, 0.1)',
                            }
                          }}
                          onMouseEnter={(e) => {
                            // Show tooltip with decision making process
                            const tooltip = document.createElement('div')
                            tooltip.innerHTML = `
                              <div style="background: rgba(0,0,0,0.95); color: white; padding: 16px; border-radius: 12px; max-width: 450px; font-size: 14px; line-height: 1.5; box-shadow: 0 8px 32px rgba(0,0,0,0.3);">
                                <strong style="color: #1976d2; font-size: 16px;">AI Decision Making Process</strong><br/><br/>
                                ${riskAnalysis.reasoning?.map((reason, index) => `<strong>${index + 1}.</strong> ${reason}`).join('<br/><br/>') || 'No detailed reasoning available from AI analysis.'}
                                <br/><br/>
                                <em style="color: #ccc; font-size: 12px;">Analysis powered by Google Gemini AI</em>
                              </div>
                            `
                            tooltip.style.position = 'absolute'
                            tooltip.style.zIndex = '10000'
                            tooltip.style.pointerEvents = 'none'
                            tooltip.style.top = `${e.clientY + 15}px`
                            tooltip.style.left = `${e.clientX + 15}px`
                            document.body.appendChild(tooltip)

                            const handleMouseLeave = () => {
                              if (document.body.contains(tooltip)) {
                                document.body.removeChild(tooltip)
                              }
                              e.target.removeEventListener('mouseleave', handleMouseLeave)
                            }
                            e.target.addEventListener('mouseleave', handleMouseLeave)

                            // Also handle mouse leave from tooltip
                            tooltip.addEventListener('mouseenter', () => {
                              // Keep tooltip visible when hovering over it
                            })

                            tooltip.addEventListener('mouseleave', () => {
                              if (document.body.contains(tooltip)) {
                                document.body.removeChild(tooltip)
                              }
                            })
                          }}
                        >
                          <InfoIcon fontSize="small" />
                        </IconButton>
                      </Box>
                    </Typography>
                    <Typography variant="body1">
                      <strong>Uncertainty:</strong> {riskAnalysis.uncertainty}%
                    </Typography>
                    <Typography variant="body1">
                      <strong>Confidence:</strong> {riskAnalysis.confidence}%
                    </Typography>
                  </Box>
                </Box>
              </Box>


              {/* Policy Parameters */}
              <Box sx={{
                p: 3,
                backgroundColor: 'rgba(255, 255, 255, 0.8)',
                borderRadius: 2,
                border: '1px solid rgba(0, 0, 0, 0.08)'
              }}>
                <Typography variant="h6" sx={{ fontWeight: 600, color: '#1976d2', mb: 3, textAlign: 'center' }}>
                  Policy Parameters
                </Typography>
                <Box sx={{ display: 'flex', flexDirection: { xs: 'column', sm: 'row' }, gap: 3, justifyContent: 'center' }}>
                  <Box sx={{ flex: { xs: 1, sm: '0 0 40%' }, p: 2, backgroundColor: 'rgba(25, 118, 210, 0.05)', borderRadius: 1, textAlign: 'center' }}>
                    <Typography variant="body2" sx={{ color: 'text.secondary', mb: 0.5 }}>
                      Premium Fee
                    </Typography>
                    <Typography variant="h6" sx={{ fontWeight: 600, color: '#1976d2' }}>
                      {riskAnalysis.fee} ALGO
                    </Typography>
                  </Box>
                  <Box sx={{ flex: { xs: 1, sm: '0 0 40%' }, p: 2, backgroundColor: 'rgba(25, 118, 210, 0.05)', borderRadius: 1, textAlign: 'center' }}>
                    <Typography variant="body2" sx={{ color: 'text.secondary', mb: 0.5 }}>
                      Coverage Amount
                    </Typography>
                    <Typography variant="h6" sx={{ fontWeight: 600, color: '#2e7d32' }}>
                      {riskAnalysis.coverage || formData.coverageAmount} ALGO
                    </Typography>
                  </Box>
                </Box>
                <Typography variant="body2" sx={{ mt: 2, color: 'text.secondary', textAlign: 'center' }}>
                  {riskAnalysis.recommendations || 'AI analysis complete. Review the parameters above and proceed to purchase if satisfied.'}
                </Typography>
              </Box>

              {!activeAddress ? (
                <Alert
                  severity="warning"
                  sx={{
                    borderRadius: 2,
                    backgroundColor: 'rgba(251, 191, 36, 0.1)',
                    border: '1px solid rgba(251, 191, 36, 0.3)'
                  }}
                >
                  Please connect your wallet to purchase a policy
                </Alert>
              ) : (
                <Button
                  fullWidth
                  variant="contained"
                  onClick={buyPolicy}
                  disabled={loading}
                  startIcon={loading ? <CircularProgress size={20} /> : null}
                  sx={{
                    py: 2,
                    fontSize: '1rem',
                    fontWeight: 600,
                    backgroundColor: '#1976d2',
                    borderRadius: 4,
                    boxShadow: '0 4px 12px rgba(25, 118, 210, 0.3)',
                    '&:hover': {
                      backgroundColor: '#1565c0',
                      boxShadow: '0 6px 16px rgba(25, 118, 210, 0.4)',
                      transform: 'translateY(-1px)',
                    },
                    transition: 'all 0.2s ease',
                  }}
                >
                  {loading ? 'Purchasing Policy...' : 'Purchase Policy'}
                </Button>
              )}
            </Box>
          ) : (
            // Policy Configuration Form
            <Box component="form" sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
            <TextField
              fullWidth
              label="ZIP Code"
              value={formData.zipCode}
              onChange={handleInputChange('zipCode')}
              placeholder="e.g., 10001"
              sx={{
                '& .MuiOutlinedInput-root': {
                  borderRadius: 3,
                  backgroundColor: 'rgba(255, 255, 255, 0.8)',
                  '&:hover': {
                    backgroundColor: 'rgba(255, 255, 255, 0.9)',
                    '& fieldset': {
                      borderColor: '#1976d2',
                    },
                  },
                  '&.Mui-focused': {
                    backgroundColor: 'rgba(255, 255, 255, 1)',
                    '& fieldset': {
                      borderColor: '#1976d2',
                      borderWidth: 2,
                    },
                  },
                },
                '& .MuiInputLabel-root': {
                  color: '#1976d2',
                  '&.Mui-focused': {
                    color: '#1565c0',
                  },
                },
              }}
            />

            <Box sx={{ display: 'flex', gap: 2 }}>
              <TextField
                fullWidth
                label="Start Date"
                type="date"
                value={formData.startDate}
                onChange={handleInputChange('startDate')}
                InputLabelProps={{ shrink: true }}
                sx={{
                  '& .MuiOutlinedInput-root': {
                    borderRadius: 3,
                    backgroundColor: 'rgba(255, 255, 255, 0.8)',
                    '&:hover': {
                      backgroundColor: 'rgba(255, 255, 255, 0.9)',
                      '& fieldset': {
                        borderColor: '#1976d2',
                      },
                    },
                    '&.Mui-focused': {
                      backgroundColor: 'rgba(255, 255, 255, 1)',
                      '& fieldset': {
                        borderColor: '#1976d2',
                        borderWidth: 2,
                      },
                    },
                  },
                  '& .MuiInputLabel-root': {
                    color: '#1976d2',
                    '&.Mui-focused': {
                      color: '#1565c0',
                    },
                  },
                }}
              />

              <TextField
                fullWidth
                label="End Date"
                type="date"
                value={formData.endDate}
                onChange={handleInputChange('endDate')}
                InputLabelProps={{ shrink: true }}
                sx={{
                  '& .MuiOutlinedInput-root': {
                    borderRadius: 3,
                    backgroundColor: 'rgba(255, 255, 255, 0.8)',
                    '&:hover': {
                      backgroundColor: 'rgba(255, 255, 255, 0.9)',
                      '& fieldset': {
                        borderColor: '#1976d2',
                      },
                    },
                    '&.Mui-focused': {
                      backgroundColor: 'rgba(255, 255, 255, 1)',
                      '& fieldset': {
                        borderColor: '#1976d2',
                        borderWidth: 2,
                      },
                    },
                  },
                  '& .MuiInputLabel-root': {
                    color: '#1976d2',
                    '&.Mui-focused': {
                      color: '#1565c0',
                    },
                  },
                }}
              />
            </Box>

            <TextField
              fullWidth
              label="Coverage Amount (ALGO)"
              type="number"
              value={formData.coverageAmount}
              onChange={handleInputChange('coverageAmount')}
              placeholder="e.g., 100"
              sx={{
                '& .MuiOutlinedInput-root': {
                  borderRadius: 3,
                  backgroundColor: 'rgba(255, 255, 255, 0.8)',
                  '&:hover': {
                    backgroundColor: 'rgba(255, 255, 255, 0.9)',
                    '& fieldset': {
                      borderColor: '#1976d2',
                    },
                  },
                  '&.Mui-focused': {
                    backgroundColor: 'rgba(255, 255, 255, 1)',
                    '& fieldset': {
                      borderColor: '#1976d2',
                      borderWidth: 2,
                    },
                  },
                },
                '& .MuiInputLabel-root': {
                  color: '#1976d2',
                  '&.Mui-focused': {
                    color: '#1565c0',
                  },
                },
              }}
            />

            <TextField
              fullWidth
              label="Description"
              multiline
              rows={4}
              value={formData.description}
              onChange={handleInputChange('description')}
              placeholder="Describe the risk you want to insure against..."
              sx={{
                '& .MuiOutlinedInput-root': {
                  borderRadius: 3,
                  backgroundColor: 'rgba(255, 255, 255, 0.8)',
                  '&:hover': {
                    backgroundColor: 'rgba(255, 255, 255, 0.9)',
                    '& fieldset': {
                      borderColor: '#1976d2',
                    },
                  },
                  '&.Mui-focused': {
                    backgroundColor: 'rgba(255, 255, 255, 1)',
                    '& fieldset': {
                      borderColor: '#1976d2',
                      borderWidth: 2,
                    },
                  },
                },
                '& .MuiInputLabel-root': {
                  color: '#1976d2',
                  '&.Mui-focused': {
                    color: '#1565c0',
                  },
                },
              }}
            />

            <Button
              fullWidth
              variant="contained"
              onClick={analyzeRisk}
              disabled={analyzing}
              startIcon={analyzing ? <CircularProgress size={20} /> : null}
              sx={{
                mt: 2,
                py: 2,
                fontSize: '1rem',
                fontWeight: 600,
                backgroundColor: '#1976d2',
                borderRadius: 4,
                boxShadow: '0 4px 12px rgba(25, 118, 210, 0.3)',
                '&:hover': {
                  backgroundColor: '#1565c0',
                  boxShadow: '0 6px 16px rgba(25, 118, 210, 0.4)',
                  transform: 'translateY(-1px)',
                },
                transition: 'all 0.2s ease',
              }}
            >
              {analyzing ? 'Analyzing Risk...' : 'Start AI Analysis'}
            </Button>
            </Box>
          )}
        </Box>
      </Box>
    </Box>
  )
}

export default GuardTab
