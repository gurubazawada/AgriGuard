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
  Container
} from '@mui/material'
import { styled } from '@mui/material/styles'
import ConnectWallet from './components/ConnectWallet'
import GuardTab from './components/GuardTab'
import ClaimTab from './components/ClaimTab'
import { getAlgodConfigFromViteEnvironment, getKmdConfigFromViteEnvironment } from './utils/network/getAlgoClientConfigs'

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
const GradientBackground = styled(Box)({
  position: 'fixed',
  top: 0,
  left: 0,
  width: '100vw',
  height: '100vh',
  background: 'linear-gradient(135deg, #f5f5f5 0%, #e8eaf6 25%, #f3e5f5 50%, #e8f5e8 75%, #f5f5f5 100%)',
  backgroundAttachment: 'fixed',
  backgroundSize: 'cover',
  zIndex: -1,
})

// Global styles to override default browser styling
const GlobalStyles = styled('style')`
  * {
    box-sizing: border-box;
  }

  html, body {
    margin: 0 !important;
    padding: 0 !important;
    width: 100% !important;
    height: 100% !important;
    overflow-x: hidden !important;
    background: linear-gradient(135deg, #f5f5f5 0%, #e8eaf6 25%, #f3e5f5 50%, #e8f5e8 75%, #f5f5f5 100%) !important;
  }

  #root {
    width: 100% !important;
    height: 100% !important;
    min-height: 100vh !important;
  }
`

const TranslucentAppBar = styled(AppBar)(({ theme }) => ({
  backgroundColor: 'rgba(255, 255, 255, 0.98)',
  backdropFilter: 'blur(20px)',
  color: theme.palette.text.primary,
  boxShadow: '0 4px 20px rgba(0, 0, 0, 0.08), 0 2px 8px rgba(0, 0, 0, 0.04)',
  borderBottom: '1px solid rgba(0, 0, 0, 0.08)',
  borderRadius: '16px 16px 16px 16px',
  position: 'relative',
  zIndex: 10,
}))

const TranslucentPaper = styled(Paper)(({ theme }) => ({
  backgroundColor: 'rgba(255, 255, 255, 0.95)',
  backdropFilter: 'blur(15px)',
  border: '1px solid rgba(0, 0, 0, 0.08)',
  boxShadow: '0 8px 32px rgba(0, 0, 0, 0.08), 0 4px 16px rgba(0, 0, 0, 0.04)',
  position: 'relative',
  zIndex: 5,
  borderRadius: 12,
}))

const StyledToggleButtonGroup = styled(ToggleButtonGroup)(({ theme }) => ({
  backgroundColor: 'rgba(255, 255, 255, 0.9)',
  borderRadius: theme.spacing(3),
  padding: theme.spacing(0.5),
  backdropFilter: 'blur(15px)',
  border: '1px solid rgba(0, 0, 0, 0.08)',
  boxShadow: '0 4px 20px rgba(0, 0, 0, 0.06), 0 2px 8px rgba(0, 0, 0, 0.04)',
  position: 'relative',
  zIndex: 15,
  '& .MuiToggleButton-root': {
    border: 'none',
    borderRadius: theme.spacing(2.5),
    padding: theme.spacing(1.5, 4),
    color: theme.palette.text.primary,
    fontWeight: 600,
    fontSize: '1rem',
    textTransform: 'none',
    transition: 'all 0.2s ease',
    '&.Mui-selected': {
      backgroundColor: '#1976d2',
      color: 'white',
      boxShadow: '0 4px 12px rgba(25, 118, 210, 0.3)',
      '&:hover': {
        backgroundColor: '#1565c0',
        boxShadow: '0 6px 16px rgba(25, 118, 210, 0.4)',
      },
    },
    '&:hover': {
      backgroundColor: 'rgba(25, 118, 210, 0.08)',
      borderRadius: theme.spacing(2.5),
    },
  },
}))

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
            backgroundColor: '#1976d2',
            color: 'white',
            fontWeight: 600,
            fontSize: '0.9rem',
            borderRadius: 4,
            px: 2,
            py: 1,
            boxShadow: '0 4px 12px rgba(25, 118, 210, 0.3)',
            '&:hover': {
              backgroundColor: '#1565c0',
              boxShadow: '0 6px 16px rgba(25, 118, 210, 0.4)',
              transform: 'translateY(-1px)',
            },
            cursor: 'pointer',
            transition: 'all 0.2s ease',
          }}
          onClick={openWalletModal}
        />
      )
    }

    return (
      <Button
        variant="outlined"
        onClick={openWalletModal}
        sx={{
          borderColor: '#1976d2',
          color: '#1976d2',
          borderRadius: 4,
          px: 4,
          py: 1.5,
          fontWeight: 600,
          fontSize: '1rem',
          borderWidth: 1,
          '&:hover': {
            borderColor: '#1565c0',
            backgroundColor: 'rgba(25, 118, 210, 0.08)',
            transform: 'translateY(-1px)',
          },
          transition: 'all 0.2s ease',
        }}
      >
        Connect Wallet
      </Button>
    )
  }

  return (
    <>
      <GlobalStyles />
      <SnackbarProvider maxSnack={3}>
        <WalletProvider manager={walletManager}>
          <Box sx={{
            position: 'relative',
            minHeight: '100vh',
            width: '100vw',
            overflowX: 'hidden'
          }}>
            <GradientBackground />
              <Container maxWidth="lg">
              <TranslucentAppBar position="static" elevation={0}>
                  <Toolbar sx={{ py: 1 }}>
                <Typography
                  variant="h5"
                  component="div"
                  sx={{
                    flexGrow: 1,
                    fontWeight: 700,
                    background: 'linear-gradient(45deg, #1976d2, #1565c0)',
                    backgroundClip: 'text',
                    WebkitBackgroundClip: 'text',
                    WebkitTextFillColor: 'transparent',
                  }}
                >
                  AgriGuard Insurance
                </Typography>

                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                  <StyledToggleButtonGroup
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
                  </StyledToggleButtonGroup>

                  <WalletButton />
                </Box>
                  </Toolbar>
                </TranslucentAppBar>
              </Container>

              <Container maxWidth="lg" sx={{ py: 4 }}>
                <TranslucentPaper sx={{
                  p: 3,
                  borderRadius: 6,
                  boxShadow: '0 20px 60px rgba(0, 0, 0, 0.15), 0 0 40px rgba(25, 118, 210, 0.12), inset 0 1px 0 rgba(255, 255, 255, 0.7)',
                  border: '1px solid rgba(255, 255, 255, 0.3)',
                  position: 'relative',
                  transform: 'translateY(0)',
                  transition: 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
                  '&:hover': {
                    transform: 'translateY(-3px)',
                    boxShadow: '0 25px 70px rgba(0, 0, 0, 0.18), 0 0 50px rgba(25, 118, 210, 0.15), inset 0 1px 0 rgba(255, 255, 255, 0.8)',
                  },
                }}>
                  {activeView === 'guard' ? <GuardTab /> : <ClaimTab />}
                </TranslucentPaper>
              </Container>

              <ConnectWallet
                openModal={walletModalOpen}
                closeModal={closeWalletModal}
              />
          </Box>
        </WalletProvider>
      </SnackbarProvider>
    </>
  )
}