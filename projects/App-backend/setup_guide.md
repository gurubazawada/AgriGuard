# 🚜 AgriGuard Smart Contract Redeployment Guide

## 📋 Overview

This guide walks you through redeploying the AgriGuard smart contracts with the new cross-contract communication features that enable automatic payouts when disputes are resolved, and policy processing/deletion capabilities.

## 🎯 New Features Added

### Cross-Contract Communication
- **Dispute Resolution → Insurance Payout**: When a dispute gets voted on and approved, it automatically triggers payout via the insurance contract
- **Automatic Settlement**: No manual intervention needed - blockchain handles the entire flow

### Policy Lifecycle Management
- **Policy Processing**: Mark policies as processed/deleted after settlement
- **Dispute Processing**: Mark disputes as processed after resolution
- **Statistics Tracking**: Comprehensive metrics for processed items

---

## 🛠️ Step-by-Step Redeployment

### Step 1: Prepare Environment

```bash
# Navigate to the contracts directory
cd /Users/gurubazawada/Desktop/AgriGuard/App/projects/App-contracts

# Ensure you have the latest code
git pull origin main

# Install/update dependencies
poetry install
```

### Step 2: Build Smart Contracts

```bash
# Build both contracts with the new features
algokit project run build

# Verify build artifacts
ls -la smart_contracts/artifacts/
```

### Step 3: Start Local Network

```bash
# Start LocalNet for testing
algokit localnet start

# Wait for network to be ready
sleep 10

# Check network status
algokit localnet status
```

### Step 4: Deploy Insurance Contract

```bash
# Deploy insurance contract first
cd smart_contracts
algokit project deploy localnet --contract insurance

# Note the deployed App ID (e.g., 123456)
# This will be needed for the dispute contract
```

### Step 5: Deploy Dispute Contract

```bash
# Deploy dispute contract
algokit project deploy localnet --contract dispute

# Note the deployed App ID (e.g., 123457)
```

### Step 6: Configure Contract Relationships

```bash
# Get your account address (this will be the admin)
algokit account new --name admin

# Set the insurance contract address in dispute contract
algokit project run setup-contracts --insurance-app-id <INSURANCE_APP_ID> --dispute-app-id <DISPUTE_APP_ID>
```

### Step 7: Set Oracle Account

```bash
# Create oracle account for automated settlements
algokit account new --name oracle

# Set oracle in insurance contract
curl -X POST http://localhost:8000/set-oracle \
  -H "Content-Type: application/json" \
  -d '{"oracle_address": "YOUR_ORACLE_ADDRESS"}'

# Link dispute contract to insurance contract
algokit project run link-contracts --dispute-app-id <DISPUTE_APP_ID> --insurance-app-id <INSURANCE_APP_ID>
```

### Step 8: Update Frontend Configuration

```bash
# Update environment variables
cd ../App-frontend

# Edit .env.localnet file
echo "VITE_APP_ID=<INSURANCE_APP_ID>" > .env.localnet
echo "VITE_DISPUTE_APP_ID=<DISPUTE_APP_ID>" >> .env.localnet
echo "VITE_ORACLE_ADDRESS=<ORACLE_ADDRESS>" >> .env.localnet
```

### Step 9: Test Cross-Contract Communication

```bash
# Start backend server
cd ../App-backend
python main.py &

# Test contract connectivity
curl http://localhost:8000/get-oracle

# Test dispute creation
curl -X POST http://localhost:8000/test-dispute-flow \
  -H "Content-Type: application/json" \
  -d '{"policy_id": 1, "test_mode": true}'
```

### Step 10: Frontend Testing

```bash
# Start frontend
cd ../App-frontend
npm run dev

# Test the complete flow:
# 1. Create a policy
# 2. File a claim
# 3. Dispute the claim
# 4. Register as juror
# 5. Vote on dispute
# 6. Verify automatic payout
```

---

## 🔧 Manual Contract Setup (Alternative)

If you prefer manual setup:

### Insurance Contract Setup

```bash
# 1. Deploy insurance contract
algokit goal app create --creator <ADMIN_ADDRESS> \
  --approval-prog artifacts/insurance/approval.teal \
  --clear-prog artifacts/insurance/clear.teal \
  --global-byteslices 1 \
  --global-ints 1 \
  --local-byteslices 0 \
  --local-ints 0 \
  --app-arg "addr:<ADMIN_ADDRESS>"

# 2. Set oracle account
algokit goal app call --app-id <INSURANCE_APP_ID> \
  --from <ADMIN_ADDRESS> \
  --app-arg "str:set_oracle" \
  --app-arg "addr:<ORACLE_ADDRESS>"
```

### Dispute Contract Setup

```bash
# 1. Deploy dispute contract
algokit goal app create --creator <ADMIN_ADDRESS> \
  --approval-prog artifacts/dispute/approval.teal \
  --clear-prog artifacts/dispute/clear.teal \
  --global-byteslices 2 \
  --global-ints 2 \
  --local-byteslices 1 \
  --local-ints 1 \
  --app-arg "addr:<ADMIN_ADDRESS>"

# 2. Link to insurance contract
algokit goal app call --app-id <DISPUTE_APP_ID> \
  --from <ADMIN_ADDRESS> \
  --app-arg "str:set_insurance_contract" \
  --app-arg "addr:<INSURANCE_APP_ID>"
```

---

## 🧪 Testing the New Features

### Test 1: Cross-Contract Communication

```bash
# 1. Create a policy
# 2. Submit a claim
# 3. Dispute the claim (this creates a dispute in dispute contract)
# 4. Register multiple jurors
# 5. Vote on the dispute
# 6. When 7+ votes are cast with majority approval:
#    - Dispute contract automatically calls insurance contract
#    - Insurance contract processes the payout
#    - Funds are transferred to policy holder
```

### Test 2: Policy Processing

```bash
# After settlement, mark policy as processed
curl -X POST http://localhost:8000/process-policy \
  -H "Content-Type: application/json" \
  -d '{"policy_id": 1}'

# Verify policy is marked as processed
curl http://localhost:8000/get-processed-policies
```

### Test 3: Dispute Processing

```bash
# After dispute resolution, mark dispute as processed
curl -X POST http://localhost:8000/process-dispute \
  -H "Content-Type: application/json" \
  -d '{"dispute_id": 1}'

# Verify dispute is marked as processed
curl http://localhost:8000/get-processed-disputes
```

---

## 📊 New Contract Methods

### Insurance Contract Additions

```python
# Mark policy as processed/deleted
mark_policy_processed(policy_id: ARC4UInt64) -> ARC4UInt64

# Get processed policies count
get_processed_policies() -> Tuple[ARC4UInt64, ARC4UInt64]
```

### Dispute Contract Additions

```python
# Cross-contract communication
_trigger_insurance_settlement(policy_id, dispute_status) -> None

# Mark dispute as processed
mark_dispute_processed(dispute_id: ARC4UInt64) -> ARC4UInt64

# Trigger policy processing
trigger_policy_processing(policy_id: ARC4UInt64) -> ARC4UInt64
```

---

## 🔐 Security Considerations

### Access Control
- Only admin can mark policies/disputes as processed
- Only assigned jurors can vote on specific disputes
- Oracle account validation for automated settlements

### Transaction Fees
- Cross-contract calls include appropriate fee allocation
- Inner transactions handle gas costs efficiently
- Fee optimization for production deployment

### State Management
- Proper validation before state changes
- Event logging for all critical operations
- Comprehensive error handling

---

## 📈 Performance Optimizations

### Gas Efficiency
- Inner transactions reduce external calls
- Optimized data structures for Box storage
- Efficient juror assignment algorithms

### Scalability
- Box storage scales with usage
- Parallel dispute processing
- Optimized query methods

---

## 🐛 Troubleshooting

### Common Issues

**Issue**: Cross-contract calls failing
```bash
# Check contract addresses are set correctly
curl http://localhost:8000/get-oracle
curl http://localhost:8000/get-insurance-contract
```

**Issue**: Disputes not showing assigned jurors
```bash
# Verify juror registration and dispute creation
curl http://localhost:8000/debug-juror-status
curl http://localhost:8000/debug-dispute-status
```

**Issue**: Payouts not processing
```bash
# Check oracle permissions and contract linkage
curl http://localhost:8000/verify-contract-linkage
```

### Debug Commands

```bash
# Check contract health
algokit project run health-check

# View contract state
algokit goal app read --app-id <APP_ID> --global

# Check transaction history
algokit indexer lookup transactions --address <CONTRACT_ADDRESS>
```

---

## 🎉 Success Checklist

- [ ] ✅ Insurance contract deployed with new features
- [ ] ✅ Dispute contract deployed with cross-contract communication
- [ ] ✅ Contract addresses linked correctly
- [ ] ✅ Oracle account configured
- [ ] ✅ Frontend environment updated
- [ ] ✅ Backend API endpoints working
- [ ] ✅ Cross-contract communication tested
- [ ] ✅ Policy processing functionality verified
- [ ] ✅ Dispute resolution flow working end-to-end

---

## 📞 Support

If you encounter issues during redeployment:

1. Check the troubleshooting section above
2. Verify all contract addresses are correct
3. Ensure oracle account has proper permissions
4. Test individual components before full integration
5. Check Algorand network connectivity

**The new cross-contract communication enables fully automated dispute resolution with instant payouts!** 🚜✨
