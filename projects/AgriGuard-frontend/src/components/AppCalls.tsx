import { useWallet } from '@txnlab/use-wallet-react'
import { useSnackbar } from 'notistack'
import { useState } from 'react'
import { AgriGuardInsuranceFactory } from '../contracts/AgriGuardInsurance'
import { OnSchemaBreak, OnUpdate } from '@algorandfoundation/algokit-utils/types/app'
import { getAlgodConfigFromViteEnvironment, getIndexerConfigFromViteEnvironment } from '../utils/network/getAlgoClientConfigs'
import { AlgorandClient } from '@algorandfoundation/algokit-utils'

interface AppCallsInterface {
  openModal: boolean
  setModalState: (value: boolean) => void
}

const AppCalls = ({ openModal, setModalState }: AppCallsInterface) => {
  const [loading, setLoading] = useState<boolean>(false)
  const [contractInput, setContractInput] = useState<string>('')
  const { enqueueSnackbar } = useSnackbar()
  const { transactionSigner, activeAddress } = useWallet()

  const algodConfig = getAlgodConfigFromViteEnvironment()
  const indexerConfig = getIndexerConfigFromViteEnvironment()
  const algorand = AlgorandClient.fromConfig({
    algodConfig,
    indexerConfig,
  })
  algorand.setDefaultSigner(transactionSigner)

  const sendAppCall = async () => {
    setLoading(true)

    // Use the already deployed contract
    const appId = Number(import.meta.env.VITE_APP_ID)
    const appAddress = import.meta.env.VITE_APP_ADDRESS

    if (!appId || !appAddress) {
      enqueueSnackbar('Contract configuration missing. Please check environment variables.', { variant: 'error' })
      setLoading(false)
      return
    }

    try {
      // Use the generated contract factory to create a client for the deployed contract
      const factory = new AgriGuardInsuranceFactory({
        defaultSender: activeAddress ?? undefined,
        algorand,
      })

      // Create app client for the deployed contract using the correct method
      const appClient = factory.getAppClientById({
        appId: appId,
        signer: transactionSigner
      })

      // Test the contract by calling getGlobals
      const response = await appClient.send.getGlobals({ args: [] })

      if (response.return) {
        const [admin, oracle, nextPolicyId] = response.return
        enqueueSnackbar(`Contract connected! Admin: ${admin}, Oracle: ${oracle}, Next Policy ID: ${nextPolicyId}`, { variant: 'success' })
      } else {
        enqueueSnackbar('Contract connected but no global state returned', { variant: 'info' })
      }
    } catch (e: any) {
      enqueueSnackbar(`Error calling the contract: ${e.message}`, { variant: 'error' })
    }

    setLoading(false)
  }

  return (
    <dialog id="appcalls_modal" className={`modal ${openModal ? 'modal-open' : ''} bg-slate-200`}>
      <form method="dialog" className="modal-box">
        <h3 className="font-bold text-lg">Test AgriGuard Insurance Contract</h3>
        <br />
        <p className="text-sm text-gray-600">
          This will connect to the deployed contract (ID: {import.meta.env.VITE_APP_ID}) and fetch its global state.
        </p>
        <br />
        <div className="modal-action ">
          <button className="btn" onClick={() => setModalState(!openModal)}>
            Close
          </button>
          <button className={`btn`} onClick={sendAppCall}>
            {loading ? <span className="loading loading-spinner" /> : 'Test Contract Connection'}
          </button>
        </div>
      </form>
    </dialog>
  )
}

export default AppCalls
