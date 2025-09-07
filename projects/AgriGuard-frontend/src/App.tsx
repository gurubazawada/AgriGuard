import { SupportedWallet, WalletId, WalletManager, WalletProvider, useWallet } from '@txnlab/use-wallet-react'
import { SnackbarProvider } from 'notistack'
import { useState } from 'react'
import {
  Box,
  AppBar,
  Toolbar,
  Typography,
  Button,
  Chip,
  ToggleButton,
  ToggleButtonGroup,
  Paper,
  Container,
  createTheme,
  ThemeProvider,
  CssBaseline
} from '@mui/material'
import { styled } from '@mui/material/styles'
import ConnectWallet from './components/ConnectWallet'
import GuardTab from './components/GuardTab'
import ClaimTab from './components/ClaimTab'
import { getAlgodConfigFromViteEnvironment, getKmdConfigFromViteEnvironment } from './utils/network/getAlgoClientConfigs'

// Minimalistic theme
const theme = createTheme({
  palette: {
    primary: {
      main: '#000000',
      light: '#333333',
      dark: '#000000',
    },
    secondary: {
      main: '#666666',
      light: '#999999',
      dark: '#333333',
    },
    background: {
      default: '#ffffff',
      paper: '#ffffff',
    },
    text: {
      primary: '#000000',
      secondary: '#666666',
    },
  },
  typography: {
    fontFamily: '"Inter", "SF Pro Display", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif',
    h1: {
      fontWeight: 300,
      fontSize: '2.5rem',
      letterSpacing: '-0.02em',
    },
    h2: {
      fontWeight: 300,
      fontSize: '2rem',
      letterSpacing: '-0.01em',
    },
    h3: {
      fontWeight: 400,
      fontSize: '1.5rem',
      letterSpacing: '-0.01em',
    },
    h4: {
      fontWeight: 400,
      fontSize: '1.25rem',
    },
    h5: {
      fontWeight: 500,
      fontSize: '1.125rem',
    },
    h6: {
      fontWeight: 500,
      fontSize: '1rem',
    },
    body1: {
      fontSize: '0.875rem',
      lineHeight: 1.6,
    },
    body2: {
      fontSize: '0.8125rem',
      lineHeight: 1.5,
    },
  },
  shape: {
    borderRadius: 8,
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          fontWeight: 500,
          borderRadius: 6,
          padding: '8px 16px',
          fontSize: '0.875rem',
        },
        contained: {
          boxShadow: 'none',
          '&:hover': {
            boxShadow: '0 2px 8px rgba(0, 0, 0, 0.15)',
          },
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)',
          border: '1px solid #f0f0f0',
        },
      },
    },
    MuiToggleButton: {
      styleOverrides: {
        root: {
          border: 'none',
          borderRadius: 6,
          padding: '8px 16px',
          fontWeight: 500,
          fontSize: '0.875rem',
          '&.Mui-selected': {
            backgroundColor: '#000000',
            color: '#ffffff',
            '&:hover': {
              backgroundColor: '#333333',
            },
          },
          '&:hover': {
            backgroundColor: '#f5f5f5',
          },
        },
      },
    },
  },
})

// Configure supported wallets
let supportedWallets: SupportedWallet[]
if (import.meta.env.VITE_ALGOD_NETWORK === 'localnet') {
  const kmdConfig = getKmdConfigFromViteEnvironment()
  supportedWallets = [
    {
      id: WalletId.KMD,
      options: {
        baseServer: kmdConfig.server,
        token: String(kmdConfig.token),
        port: String(kmdConfig.port),
      },
    },
  ]
} else {
  supportedWallets = [
    { id: WalletId.DEFLY },
    { id: WalletId.PERA },
    { id: WalletId.EXODUS },
  ]
}

// Styled components
const MinimalAppBar = styled(AppBar)({
  backgroundColor: '#ffffff',
  color: '#000000',
  boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)',
  borderBottom: '1px solid #f0f0f0',
})

const MinimalPaper = styled(Paper)({
  backgroundColor: '#ffffff',
  borderRadius: 8,
  border: '1px solid #f0f0f0',
  boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)',
})

const MinimalToggleGroup = styled(ToggleButtonGroup)({
  backgroundColor: '#f8f8f8',
  borderRadius: 6,
  padding: 4,
  '& .MuiToggleButton-root': {
    border: 'none',
    borderRadius: 4,
    padding: '8px 16px',
    fontWeight: 500,
    fontSize: '0.875rem',
    '&.Mui-selected': {
      backgroundColor: '#000000',
      color: '#ffffff',
      '&:hover': {
        backgroundColor: '#333333',
      },
    },
    '&:hover': {
      backgroundColor: '#f0f0f0',
    },
  },
})

export default function App() {
  const [activeView, setActiveView] = useState<'guard' | 'claim'>('guard')
  const [walletModalOpen, setWalletModalOpen] = useState(false)
  const algodConfig = getAlgodConfigFromViteEnvironment()

  const walletManager = new WalletManager({
    wallets: supportedWallets,
    defaultNetwork: algodConfig.network,
    networks: {
      [algodConfig.network]: {
        algod: {
          baseServer: algodConfig.server,
          port: algodConfig.port,
          token: String(algodConfig.token),
        },
      },
    },
    options: {
      resetNetwork: true,
    },
  })

  const handleViewChange = (
    event: React.MouseEvent<HTMLElement>,
    newView: 'guard' | 'claim' | null,
  ) => {
    if (newView !== null) {
      setActiveView(newView)
    }
  }

  const openWalletModal = () => setWalletModalOpen(true)
  const closeWalletModal = () => setWalletModalOpen(false)

  const WalletButton = () => {
    const { activeAddress } = useWallet()

    if (activeAddress) {
      return (
        <Chip
          label={`${activeAddress.slice(0, 6)}...${activeAddress.slice(-4)}`}
          sx={{
            backgroundColor: '#000000',
            color: '#ffffff',
            fontWeight: 500,
            fontSize: '0.875rem',
            borderRadius: 6,
            px: 2,
            py: 1,
            '&:hover': {
              backgroundColor: '#333333',
            },
            cursor: 'pointer',
          }}
          onClick={openWalletModal}
        />
      )
    }

    return (
      <Button
        variant="contained"
        onClick={openWalletModal}
        sx={{
          backgroundColor: '#000000',
          color: '#ffffff',
          borderRadius: 6,
          px: 3,
          py: 1,
          fontWeight: 500,
          fontSize: '0.875rem',
          '&:hover': {
            backgroundColor: '#333333',
          },
        }}
      >
        Connect Wallet
      </Button>
    )
  }

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <SnackbarProvider maxSnack={3}>
        <WalletProvider manager={walletManager}>
          <Box sx={{
            minHeight: '100vh',
            backgroundColor: '#ffffff',
          }}>
            <MinimalAppBar position="static" elevation={0}>
              <Container maxWidth="lg">
                <Toolbar sx={{ 
                  justifyContent: 'space-between',
                  py: 2,
                  px: 0,
                }}>
                  <Typography 
                    variant="h5" 
                    component="div" 
                    sx={{ 
                      fontWeight: 300,
                      color: '#000000',
                    }}
                  >
                    AgriGuard
                  </Typography>
                  
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 3 }}>
                    <MinimalToggleGroup
                      value={activeView}
                      exclusive
                      onChange={handleViewChange}
                      aria-label="view toggle"
                    >
                      <ToggleButton value="guard" aria-label="guard">
                        Policy
                      </ToggleButton>
                      <ToggleButton value="claim" aria-label="claim">
                        Claims
                      </ToggleButton>
                    </MinimalToggleGroup>
                    
                    <WalletButton />
                  </Box>
                </Toolbar>
              </Container>
            </MinimalAppBar>

            <Container maxWidth="lg" sx={{ py: 4 }}>
              <MinimalPaper sx={{
                p: 4,
                minHeight: '70vh',
              }}>
                {activeView === 'guard' ? <GuardTab /> : <ClaimTab />}
              </MinimalPaper>
            </Container>

            <ConnectWallet
              openModal={walletModalOpen}
              closeModal={closeWalletModal}
            />
          </Box>
        </WalletProvider>
      </SnackbarProvider>
    </ThemeProvider>
  )
}