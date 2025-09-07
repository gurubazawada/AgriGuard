# AgriGuard Insurance Backend API

FastAPI server that handles LLM risk analysis and smart contract interactions for AgriGuard Insurance.

## Features

- **LLM Risk Analysis**: Analyzes natural language descriptions of agricultural risks
- **Smart Contract Integration**: Calculates fees and creates policies
- **CORS Enabled**: Works with the React frontend
- **Mock Implementation**: Ready for real LLM and blockchain integration

## Setup

1. **Install dependencies**:
   ```bash
   cd App/projects/App-backend
   pip install -r requirements.txt
   ```

2. **Configure API Keys**:
   ```bash
   # Copy the environment template
   cp env_template.txt .env
   
   # Edit .env and add your Google API key
   # Get your API key from: https://aistudio.google.com/app/apikey
   ```

3. **Start the server**:
   ```bash
   python start_server.py
   ```

4. **Access the API**:
   - Server: http://localhost:8000
   - Documentation: http://localhost:8000/docs
   - Interactive API: http://localhost:8000/redoc

## API Endpoints

### POST `/analyze-risk`
Analyzes agricultural risk using LLM and generates policy parameters.

**Request**:
```json
{
  "description": "I want to insure my corn crop against drought...",
  "zipCode": "10001",
  "startTime": "2024-01-01T00:00:00Z",
  "endTime": "2024-12-31T23:59:59Z",
  "cap": "1000"
}
```

**Response**:
```json
{
  "risk_score": 75,
  "uncertainty": 0.25,
  "direction": 1,
  "threshold": "2.5",
  "slope": "3.2",
  "fee": "1500000",
  "reasoning": "Risk analysis completed with 87.5% confidence",
  "reasoning_steps": [
    "Step 1: Analyzed crop type (corn) and location (Iowa)",
    "Step 2: Searched current drought conditions in the region",
    "Step 3: Calculated historical risk factors for corn in Iowa"
  ],
  "web_sources": [
    "weather.com",
    "usda.gov",
    "drought.gov"
  ],
  "confidence": 0.875,
  "analysis_summary": "High risk of drought conditions based on current weather patterns and historical data"
}
```

### POST `/create-policy`
Creates insurance policy by calling smart contract.

**Request**:
```json
{
  "userAddress": "ABC123...",
  "zipCode": "10001",
  "startTime": "2024-01-01T00:00:00Z",
  "endTime": "2024-12-31T23:59:59Z",
  "cap": "1000",
  "direction": 1,
  "threshold": "2.5",
  "slope": "3.2",
  "fee": "1500000",
  "description": "Corn crop insurance..."
}
```

**Response**:
```json
{
  "policyId": "POL-123456",
  "transactionHash": "0xabc123...",
  "status": "success"
}
```

### GET `/policies/{user_address}`
Get all policies for a specific user.

## Next Steps

1. **Integrate Real LLM**: Replace mock analysis with OpenAI/Anthropic API
2. **Smart Contract Integration**: Connect to actual Algorand network
3. **Payment Processing**: Implement real payment transactions
4. **Database**: Add persistent storage for policies
5. **Authentication**: Add user authentication and authorization

## Environment Variables

Create a `.env` file:
```env
ALGORAND_NETWORK=localnet
ALGORAND_NODE_URL=http://localhost:4001
ALGORAND_TOKEN=aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
OPENAI_API_KEY=your_openai_key_here
```
