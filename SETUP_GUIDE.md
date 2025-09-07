# 🌾 AgriGuard Insurance - Complete Setup Guide

## 🚀 Quick Start

### 1. **Set up Google API Key**

1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Create a new API key
3. Copy the key

### 2. **Configure Backend**

```bash
cd App/projects/App-backend

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp env_template.txt .env

# Edit .env and add your API key
# GOOGLE_API_KEY=your_actual_api_key_here
```

### 3. **Start All Services**

```bash
# From the App directory
./start_all.sh
```

**OR start individually:**

```bash
# Terminal 1 - Backend
cd App/projects/App-backend
python start_server.py

# Terminal 2 - Frontend
cd App/projects/App-frontend
npm run dev

# Terminal 3 - LocalNet (if needed)
cd App/projects/App-contracts
source .venv/bin/activate
algokit localnet start
```

## 📍 Access Points

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **LocalNet Explorer**: http://localhost:4001

## 🔧 Features

### ✨ **Enhanced Risk Analysis**
- **Web Search Grounding**: Gemini searches real-time agricultural data
- **Step-by-step Reasoning**: Detailed analysis steps with hover tooltips
- **Confidence Scoring**: AI confidence levels for risk assessments
- **Source Attribution**: Links to web sources used in analysis

### 🎨 **Beautiful UI**
- **Green Gradient Background**: Agricultural theme
- **Floating Bubble Buttons**: Modern glass morphism design
- **Interactive Tooltips**: Hover for detailed information
- **Expandable Sections**: Detailed reasoning steps
- **Real-time Feedback**: Loading states and progress indicators

### 🔄 **Complete Flow**
1. **Policy Details** → Basic information input
2. **Risk Description** → Natural language description
3. **AI Analysis** → Gemini + web search analysis
4. **Review & Pay** → Final confirmation and payment

## 🛠️ Development

### Backend Structure
```
App/projects/App-backend/
├── main.py              # FastAPI server
├── requirements.txt     # Python dependencies
├── start_server.py     # Startup script
├── .env                # Environment variables (create from template)
└── README.md           # Backend documentation
```

### Frontend Structure
```
App/projects/App-frontend/
├── src/
│   ├── components/
│   │   ├── PolicyForm.tsx    # Enhanced 4-step form
│   │   ├── PolicyList.tsx    # Policy management
│   │   └── Logo.tsx          # Logo component
│   └── App.direct.tsx        # Main app with beautiful UI
├── package.json
└── .env                      # Frontend environment
```

### Smart Contract
```
App/projects/App-contracts/
├── smart_contracts/insurance/
│   ├── contract.py           # Enhanced with calculate_fee
│   └── abi_types.py         # Policy data structures
└── deploy_config.py         # Deployment script
```

## 🔑 API Key Setup

### Google Gemini API
1. Visit [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Sign in with Google account
3. Click "Create API Key"
4. Copy the generated key
5. Add to `App/projects/App-backend/.env`:
   ```
   GOOGLE_API_KEY=your_api_key_here
   ```

## 🧪 Testing the Flow

1. **Start all services** using `./start_all.sh`
2. **Open frontend** at http://localhost:5173
3. **Connect wallet** (select from LocalNet wallets)
4. **Go to Guard tab**
5. **Fill out policy details**:
   - ZIP Code: 10001
   - Start/End dates
   - Coverage amount
6. **Describe your risk** in natural language:
   ```
   I want to insure my corn crop in Iowa against drought. 
   If rainfall drops below 2 inches per month during the 
   growing season (May-September), I should be compensated.
   ```
7. **Click "Analyze Risk"** - Watch the AI analysis with web search
8. **Review the results** - See detailed reasoning, confidence, and sources
9. **Create & Pay** - Complete the policy creation

## 🎯 Next Steps

1. **Add your logo PNG** to `App/projects/App-frontend/public/` and update `Logo.tsx`
2. **Deploy to testnet** instead of LocalNet
3. **Add real payment processing** with Algorand transactions
4. **Integrate with real weather APIs** for oracle data
5. **Add user authentication** and policy management

## 🐛 Troubleshooting

### Backend Issues
- **API Key Error**: Make sure `GOOGLE_API_KEY` is set in `.env`
- **Import Error**: Run `pip install -r requirements.txt`
- **Port Conflict**: Change port in `start_server.py`

### Frontend Issues
- **CORS Error**: Backend CORS is configured for localhost:5173
- **API Connection**: Check backend is running on port 8000
- **Wallet Connection**: Ensure LocalNet is running

### Smart Contract Issues
- **Compilation Error**: Check Python syntax in contract.py
- **Deployment Error**: Verify LocalNet is running
- **Transaction Error**: Check account has sufficient ALGO

## 📚 Documentation

- **Backend API**: http://localhost:8000/docs
- **Algorand Docs**: https://developer.algorand.org/
- **Google AI Studio**: https://aistudio.google.com/
- **Material-UI**: https://mui.com/

---

**Ready to build the future of agricultural insurance! 🌾✨**
