# 🎭 AgriGuard Demo Guide

## Overview
AgriGuard is now running in **DEMO MODE** with realistic mock data to showcase the complete application flow. The backend AI API is still live for real risk analysis, but all blockchain interactions are simulated.

## 🌟 Demo Features

### ✅ What Works (Mock + Real):
- **AI Risk Analysis** - Real Gemini API calls for authentic quotes
- **Policy Creation** - Simulated smart contract calls with realistic responses  
- **Policy Management** - View, claim, and manage policies
- **Dispute System** - File disputes and participate as a juror
- **Cross-Contract Communication** - Simulated oracle settlements and payouts
- **Realistic Data** - Pre-loaded policies and disputes for demonstration

### 🎬 Demo Data Included:
- **3 Pre-loaded Policies** with different statuses (Active, Expired, Claimable)
- **2 Sample Disputes** (one pending vote, one resolved)
- **Juror Registration** and voting functionality
- **Wallet Simulation** (no real wallet connection needed)

---

## 🎯 **Recommended Demo Flow**

### **Part 1: Policy Creation (5 minutes)**
1. **Navigate to "Guard" tab**
2. **Fill out policy form:**
   - ZIP Code: `90210` (Beverly Hills)
   - Start Date: Today
   - End Date: 30 days from now
   - Coverage: `1000` ALGO
   - Description: `"Protect against extreme heat waves in Beverly Hills during summer months"`

3. **Click "Analyze Risk"**
   - ⚡ Real AI analysis happens via Gemini API
   - Watch realistic risk scoring and fee calculation
   - Shows confidence levels and reasoning steps

4. **Click "Purchase Policy"**
   - ✅ Simulated blockchain transaction
   - Policy gets added to your portfolio
   - Shows success notifications with policy ID

### **Part 2: Policy Management (3 minutes)**
1. **Navigate to "Claims" tab**
2. **View your policies:**
   - See 4 total policies (3 pre-loaded + 1 just created)
   - Notice different statuses: Active, Expired, **Claimable**, Settled

3. **Focus on ZIP 94102 policy (San Francisco)**
   - Status shows "**CLAIMABLE**" 
   - Coverage: 8,000 ALGO
   - This represents a policy where conditions were met

### **Part 3: Claims & Disputes (7 minutes)**
1. **File a claim on the claimable policy:**
   - Click "File Claim" on ZIP 94102 policy
   - ⚡ Real AI evaluation via backend
   - Watch Oracle decision process

2. **If claim is rejected, file a dispute:**
   - Click "Dispute Claim" button
   - ✅ Creates new dispute in the system
   - Shows "Dispute Filed" status

3. **Navigate to "Vote" tab (Juror Experience):**
   - See pre-loaded disputes waiting for votes
   - View dispute details and reasoning
   - Cast votes as a community juror
   - See voting tallies update in real-time

### **Part 4: Juror System (3 minutes)**
1. **In "Vote" tab, register as juror:**
   - Click "Register as Juror" 
   - Simulates 1000 ALGO stake
   - Shows juror statistics (85% accuracy, 12 total votes)

2. **Vote on active disputes:**
   - Review dispute evidence
   - Cast YES/NO votes
   - See community consensus building
   - Experience governance in action

### **Part 5: System Integration (2 minutes)**
1. **Demonstrate cross-contract communication:**
   - Show how dispute resolutions trigger payouts
   - Oracle settlements updating policy status
   - Policy lifecycle management

2. **Highlight AI-Blockchain Integration:**
   - Real-time risk analysis 
   - Weather data integration
   - Community-driven dispute resolution

---

## 🎤 **Demo Talking Points**

### **Problem We Solve:**
- Traditional crop insurance is slow, expensive, and opaque
- Farmers need parametric insurance with instant, transparent payouts
- Current systems lack community governance and AI-driven pricing

### **Our Solution:**
- **AI-Powered Risk Analysis**: Real-time assessment using Google Gemini
- **Parametric Insurance**: Automatic payouts based on measurable conditions
- **Community Governance**: Decentralized dispute resolution by peer jurors
- **Blockchain Transparency**: All transactions and decisions are auditable

### **Technical Innovation:**
- **Algorand Smart Contracts**: Fast, cheap, and environmentally friendly
- **Cross-Contract Communication**: Insurance and dispute contracts work together
- **AI-Blockchain Bridge**: Seamless integration of AI analysis with on-chain execution
- **Event-Driven Architecture**: Real-time updates and responsive UI

### **Market Opportunity:**
- $7B+ global crop insurance market
- Underserved farmers in developing regions
- Growing demand for parametric insurance solutions
- Climate change increasing weather volatility

---

## 🛠 **Technical Demo Notes**

### **Mock Data Highlights:**
- ZIP `94102`: Claimable policy (demonstrate successful claim flow)
- ZIP `90210`: Active policy (just purchased, show in portfolio)
- ZIP `10001`: Settled policy (shows completed payout)

### **AI Integration:**
- Backend runs on `http://localhost:8000`
- Real Gemini API calls for risk analysis
- Authentic weather data integration
- Production-ready API endpoints

### **Performance:**
- Simulated network delays for realism
- Loading states and progress indicators
- Error handling and user feedback
- Responsive design for all screen sizes

---

## 🔧 **Demo Setup**

### **Before Demo:**
1. Ensure backend is running: `uvicorn main:app --reload`
2. Frontend shows "🎭 AgriGuard running in DEMO mode" in console
3. No wallet connection required - everything is simulated
4. All data resets on page refresh for clean demos

### **During Demo:**
- Point out real vs simulated components
- Emphasize the AI analysis is actually happening
- Show browser console for technical audience
- Highlight cross-contract interactions

### **Demo Variants:**
- **Technical Audience**: Focus on smart contract architecture
- **Business Audience**: Emphasize market fit and user experience  
- **Investor Audience**: Highlight scalability and revenue model
- **Farmer Audience**: Show ease of use and transparent pricing

---

## 🎨 **Visual Demo Tips**

### **Show These Screens:**
1. ✅ Policy creation with real AI analysis
2. ✅ Policy portfolio with multiple statuses
3. ✅ Claim filing and oracle decision
4. ✅ Dispute creation and community voting
5. ✅ Juror dashboard with reputation system

### **Highlight These Features:**
- Real-time risk scoring with confidence levels
- Transparent fee calculation with AI reasoning
- Community-driven dispute resolution
- Automatic settlement and payout simulation
- Cross-contract communication in action

### **Demo Flow Timing:**
- **5 min**: Policy creation and AI analysis
- **3 min**: Portfolio management
- **7 min**: Claims and disputes
- **3 min**: Juror system
- **2 min**: Integration highlights
- **Total: ~20 minutes** for full demo

---

*🎭 This demo mode provides a complete, realistic experience of AgriGuard without requiring deployed smart contracts or wallet connections. Perfect for showcasing the full application flow!*
