from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import asyncio
import json
import os
from datetime import datetime
import google.generativeai as genai
import re
from algosdk import account, mnemonic
from algosdk.atomic_transaction_composer import AtomicTransactionComposer
from algosdk.abi import Method
from algokit_utils import AlgorandClient

app = FastAPI(title="AgriGuard Insurance API", version="1.0.0")

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Data conversion utilities for smart contract compatibility
def convert_threshold_to_numeric(threshold_str: str) -> int:
    """Convert threshold string to numeric value for smart contract"""
    try:
        numbers = re.findall(r'[\d.]+', threshold_str)
        if numbers:
            value = float(numbers[0])
            # Convert to integer with appropriate scaling
            if 'inch' in threshold_str.lower() or 'mm' in threshold_str.lower():
                return int(value * 1000)
            elif 'degree' in threshold_str.lower() or 'temp' in threshold_str.lower():
                return int(value * 100)
            else:
                return int(value * 100)
        return 0
    except:
        return 0

def convert_slope_to_numeric(slope_str: str) -> int:
    """Convert slope string to numeric value for smart contract"""
    try:
        numbers = re.findall(r'[\d.]+', slope_str)
        if numbers:
            return int(float(numbers[0]) * 100)
        return 100
    except:
        return 100

def convert_algo_to_micro_algo(algo_str: str) -> int:
    """Convert ALGO string to microALGOs for smart contract"""
    try:
        algo_amount = float(algo_str)
        return int(algo_amount * 1_000_000)
    except:
        return 0

def convert_datetime_to_unix(datetime_str: str) -> int:
    """Convert datetime string to Unix timestamp"""
    try:
        dt = datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
        return int(dt.timestamp())
    except:
        return int(datetime.now().timestamp())

# Configure Gemini client
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)
else:
    raise ValueError("GOOGLE_API_KEY environment variable is required")

# Smart contract configuration
APP_ID = int(os.getenv("APP_ID", "1039"))
ALGOD_SERVER = os.getenv("ALGOD_SERVER", "http://localhost")
ALGOD_PORT = int(os.getenv("ALGOD_PORT", "4001"))
ALGOD_TOKEN = os.getenv("ALGOD_TOKEN", "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
ORACLE_MNEMONIC = os.getenv("ORACLE_MNEMONIC")

if not ORACLE_MNEMONIC:
    raise ValueError("ORACLE_MNEMONIC environment variable is required")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class RiskAnalysisRequest(BaseModel):
    description: str
    zipCode: str
    startTime: str
    endTime: str
    cap: str

class RiskAnalysisResponse(BaseModel):
    risk_score: int
    uncertainty: float
    direction: int
    threshold: str
    slope: str
    fee: str
    reasoning: str
    reasoning_steps: List[str]
    web_sources: List[str]
    confidence: float
    analysis_summary: str
    # Smart contract compatible data
    threshold_numeric: int  # Numeric value for smart contract
    slope_numeric: int      # Numeric value for smart contract
    fee_micro_algo: int     # Fee in microALGOs for smart contract
    t0_unix: int           # Start time as Unix timestamp
    t1_unix: int           # End time as Unix timestamp
    cap_micro_algo: int    # Coverage amount in microALGOs

class OracleSettlementRequest(BaseModel):
    policy_id: int
    zip_code: str
    start_date: str
    end_date: str
    coverage_amount: str
    direction: int
    threshold: int
    slope: int
    fee_paid: int
    settled: bool
    owner: str

class OracleSettlementResponse(BaseModel):
    decision: int  # 0 = reject, 1 = approve
    reasoning: str
    reasoning_steps: List[str]
    web_sources: List[str]
    confidence: float
    settlement_amount: int  # Amount to pay out (0 if rejected)
    transaction_success: bool  # Whether the smart contract call succeeded
    transaction_id: Optional[str] = None

class SetOracleRequest(BaseModel):
    oracle_address: str

class SetOracleResponse(BaseModel):
    success: bool
    transaction_id: Optional[str] = None
    oracle_address: str
    error: Optional[str] = None

@app.get("/")
async def root():
    return {"message": "AgriGuard Insurance API", "status": "running"}

async def analyze_risk_with_gemini(request: RiskAnalysisRequest):
    """Analyze agricultural risk using Gemini"""
    try:
        # Create the analysis prompt
        prompt = f"""
        You are an agricultural risk analyst for AgriGuard, a blockchain-based insurance platform on Algorand.

        CONTEXT ABOUT ALGORAND AND ALGO:
        - Algorand is a carbon-negative blockchain platform designed for real-world applications
        - ALGO is the native cryptocurrency of Algorand (1 ALGO = 1,000,000 microALGOs)
        - This insurance platform uses smart contracts to automatically pay out claims when weather conditions trigger
        - The coverage amount is denominated in ALGO tokens, which have real monetary value
        - This is a decentralized insurance system where farmers can protect against weather risks

        USER REQUEST:
        Description: {request.description}
        Location: ZIP Code {request.zipCode}
        Coverage Period: {request.startTime} to {request.endTime}
        Coverage Amount: {request.cap} ALGO

        Please provide a detailed analysis including:
        1. Current weather and agricultural conditions for this location
        2. Historical risk data for similar crops/conditions
        3. Risk score (0-100) based on probability of loss
        4. Uncertainty level (0.0-0.5) based on data availability and predictability
        5. Recommended trigger direction (1 for below threshold, 0 for above threshold)
        6. Specific threshold value based on the risk type
        7. Slope parameter for the risk curve

        Provide exactly 5 reasoning steps that explain your analysis process.

        Format your response as JSON with these exact fields:
        {{
            "risk_score": <integer 0-100>,
            "uncertainty": <float 0.0-0.5>,
            "direction": <integer 0 or 1>,
            "threshold": "<string value>",
            "slope": "<string value>",
            "reasoning_steps": [
                "Step 1: <detailed explanation>",
                "Step 2: <detailed explanation>",
                "Step 3: <detailed explanation>",
                "Step 4: <detailed explanation>",
                "Step 5: <detailed explanation>"
            ],
            "web_sources": [
                "source1.com",
                "source2.com",
                ...
            ],
            "confidence": <float 0.0-1.0>,
            "analysis_summary": "<brief summary of the analysis>"
        }}
        """

        # Configure the model
        model = genai.GenerativeModel('gemini-1.5-flash')

        # Generate content
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.3,
                max_output_tokens=2048,
            )
        )

        # Parse the JSON response
        response_text = response.text.strip()

        # Extract JSON from response (in case there's extra text)
        json_start = response_text.find('{')
        json_end = response_text.rfind('}') + 1
        json_text = response_text[json_start:json_end]

        analysis_data = json.loads(json_text)

        # Calculate fee based on risk parameters
        base_fee = int(request.cap) * 0.01  # 1% of coverage
        risk_multiplier = 1 + (analysis_data["risk_score"] / 100)
        uncertainty_multiplier = 1 + analysis_data["uncertainty"]

        # Calculate duration multiplier
        try:
            start_date = datetime.fromisoformat(request.startTime.replace('Z', '+00:00'))
            end_date = datetime.fromisoformat(request.endTime.replace('Z', '+00:00'))
            duration_days = (end_date - start_date).days
            duration_multiplier = 1 + (duration_days / 365) * 0.5  # Up to 1.5x for full year
        except (ValueError, AttributeError):
            duration_multiplier = 1.0

        fee_micro_algo = int(base_fee * risk_multiplier * uncertainty_multiplier * duration_multiplier * 1000000)

        # Convert data for smart contract compatibility
        threshold_numeric = convert_threshold_to_numeric(analysis_data["threshold"])
        slope_numeric = convert_slope_to_numeric(analysis_data["slope"])
        cap_micro_algo = convert_algo_to_micro_algo(request.cap)
        t0_unix = convert_datetime_to_unix(request.startTime)
        t1_unix = convert_datetime_to_unix(request.endTime)

        return RiskAnalysisResponse(
            risk_score=analysis_data["risk_score"],
            uncertainty=analysis_data["uncertainty"],
            direction=analysis_data["direction"],
            threshold=analysis_data["threshold"],
            slope=analysis_data["slope"],
            fee=f"{fee_micro_algo / 1_000_000:.2f}",
            reasoning=f"Risk analysis completed with {analysis_data['confidence']*100:.1f}% confidence",
            reasoning_steps=analysis_data["reasoning_steps"],
            web_sources=analysis_data["web_sources"],
            confidence=analysis_data["confidence"],
            analysis_summary=analysis_data["analysis_summary"],
            threshold_numeric=threshold_numeric,
            slope_numeric=slope_numeric,
            fee_micro_algo=fee_micro_algo,
            t0_unix=t0_unix,
            t1_unix=t1_unix,
            cap_micro_algo=cap_micro_algo
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Risk analysis failed: {str(e)}")


async def analyze_oracle_settlement_with_gemini(request: OracleSettlementRequest):
    """Use Gemini to analyze policy settlement decision"""
    try:
        # Convert coverage amount to microALGOs for calculation
        coverage_micro_algos = convert_algo_to_micro_algo(request.coverage_amount)

        # Create a detailed prompt for settlement analysis
        prompt = f"""
You are an agricultural insurance oracle analyzing a policy settlement claim on the Algorand blockchain.

POLICY DETAILS:
- Policy ID: {request.policy_id}
- Location: ZIP Code {request.zip_code}
- Coverage Period: {request.start_date} to {request.end_date}
- Coverage Amount: {request.coverage_amount} ALGO ({coverage_micro_algos:,} microALGOs)
- Risk Direction: {request.direction} (0=above threshold triggers payout, 1=below threshold triggers payout)
- Threshold: {request.threshold}
- Slope: {request.slope}
- Fee Paid: {request.fee_paid:,} microALGOs
- Policy Owner: {request.owner}

SETTLEMENT ANALYSIS REQUIRED:
Analyze whether this policy should be settled (approved for payout) or rejected.

Consider:
1. Weather data for the location and time period - check if threshold was breached
2. Agricultural conditions during the coverage period
3. Whether the risk conditions were actually met based on direction and threshold
4. Market conditions and crop prices during the period
5. Historical data for similar claims in the area

RESPONSE FORMAT (JSON):
{{
    "decision": 0 or 1,
    "reasoning": "Detailed explanation of decision",
    "reasoning_steps": [
        "Step 1: Analyzed weather data for ZIP {request.zip_code} during coverage period",
        "Step 2: Verified threshold breach conditions (direction={request.direction}, threshold={request.threshold})",
        "Step 3: Evaluated agricultural impact and market conditions",
        "Step 4: Considered historical precedents and risk factors",
        "Step 5: Made final settlement decision"
    ],
    "web_sources": ["weather.gov", "usda.gov", "noaa.gov"],
    "confidence": 0.85,
    "settlement_amount": {coverage_micro_algos if 'decision' in locals() and 'decision' == 1 else 0}
}}

IMPORTANT GUIDELINES:
- Use web search to get current and historical weather/agricultural data for ZIP {request.zip_code}
- Be conservative - only approve if clear evidence shows threshold was breached
- Decision = 1 (approve) only if weather conditions clearly met the policy trigger
- Decision = 0 (reject) if conditions were not met or evidence is insufficient
- Settlement amount = {coverage_micro_algos:,} microALGOs if approved, 0 if rejected
- Provide specific weather data sources and measurements in reasoning
"""

        model = genai.GenerativeModel('gemini-1.5-flash')

        # Enable web search grounding for real data
        response = model.generate_content(
            prompt,
            tools=[{"google_search_retrieval": {}}],
            generation_config=genai.types.GenerationConfig(
                temperature=0.2,  # Lower temperature for more consistent analysis
                max_output_tokens=2048,
            )
        )

        # Parse the response
        response_text = response.text

        # Extract JSON from the response
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if not json_match:
            raise ValueError("No JSON found in Gemini response")

        analysis_data = json.loads(json_match.group())

        # Validate and fix settlement_amount
        if analysis_data["decision"] == 1:
            analysis_data["settlement_amount"] = coverage_micro_algos
        else:
            analysis_data["settlement_amount"] = 0

        return analysis_data

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Oracle analysis failed: {str(e)}")

async def call_smart_contract_settlement(policy_id: int, decision: int, expected_payout: int) -> dict:
    """Call the smart contract's oracle_settle method and ensure payout execution"""
    try:
        # Set up Algorand client
        from algosdk.v2client import algod
        algod_client = algod.AlgodClient(ALGOD_TOKEN, f"{ALGOD_SERVER}:{ALGOD_PORT}")

        # Get oracle account from mnemonic
        oracle_private_key = mnemonic.to_private_key(ORACLE_MNEMONIC)
        oracle_address = account.address_from_private_key(oracle_private_key)

        print(f"🔑 Oracle Address: {oracle_address}")
        print(f"📋 Policy ID: {policy_id}, Decision: {decision}, Expected Payout: {expected_payout}")

        # Create AlgoKit client
        algorand = AlgorandClient.from_clients(algod_client, algod_client)

        # Create app client
        from smart_contracts.artifacts.insurance.agri_guard_insurance_client import AgriGuardInsuranceClient, APP_SPEC

        app_client = algorand.application_client(
            app_id=int(APP_ID),
            app_spec=APP_SPEC,
            sender=oracle_address
        )

        # Set the signer for the oracle
        algorand.set_default_signer(oracle_private_key)

        # First, let's check if oracle is set correctly (optional - for debugging)
        try:
            oracle_check = app_client.call(method="get_oracle")
            print(f"✅ Contract Oracle: {oracle_check.return_value}")
        except Exception as e:
            print(f"⚠️ Could not check oracle (might not be set): {e}")

        print(f"🔄 Calling oracle_settle with policy_id={policy_id}, approved={decision}")

        # Call the oracle_settle method with proper parameter types
        result = app_client.call(
            method="oracle_settle",
            args={
                "policy_id": policy_id,
                "approved": decision
            }
        )

        # The contract returns the actual payout amount
        actual_payout = result.return_value if hasattr(result, 'return_value') else expected_payout

        print(f"💰 Settlement Result - Actual Payout: {actual_payout}, Transaction ID: {result.tx_id if hasattr(result, 'tx_id') else 'N/A'}")

        # If decision was to approve but payout is 0, this indicates an issue
        if decision == 1 and actual_payout == 0:
            print("⚠️ WARNING: Decision was approve but payout amount is 0!")
            return {
                "success": False,
                "transaction_id": result.tx_id if hasattr(result, 'tx_id') else None,
                "payout_amount": 0,
                "expected_payout": expected_payout,
                "decision": decision,
                "error": "Payout amount is 0 despite approval decision"
            }

        return {
            "success": True,
            "transaction_id": result.tx_id if hasattr(result, 'tx_id') else None,
            "payout_amount": actual_payout,
            "expected_payout": expected_payout,
            "decision": decision
        }

    except Exception as e:
        print(f"❌ Smart contract settlement failed: {str(e)}")
        return {
            "success": False,
            "transaction_id": None,
            "payout_amount": 0,
            "expected_payout": expected_payout,
            "decision": decision,
            "error": str(e)
        }

@app.post("/analyze-risk", response_model=RiskAnalysisResponse)
async def analyze_risk(request: RiskAnalysisRequest):
    """Analyze agricultural risk using LLM and generate policy parameters"""
    try:
        return await analyze_risk_with_gemini(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Risk analysis failed: {str(e)}")

@app.post("/oracle-settle", response_model=OracleSettlementResponse)
async def oracle_settle(request: OracleSettlementRequest):
    """Oracle settlement endpoint - analyzes policy and makes settlement decision"""
    try:
        # Check if policy is already settled
        if request.settled:
            return OracleSettlementResponse(
                decision=0,
                reasoning="Policy is already settled",
                reasoning_steps=["Policy already settled - no action needed"],
                web_sources=[],
                confidence=1.0,
                settlement_amount=0,
                transaction_success=False,
                transaction_id=None
            )

        # Get oracle analysis from Gemini
        analysis_data = await analyze_oracle_settlement_with_gemini(request)

        decision = analysis_data["decision"]
        settlement_amount = analysis_data["settlement_amount"]

        # Call smart contract if decision is to approve
        transaction_success = False
        transaction_id = None
        actual_payout = 0

        if decision == 1:
            # Only call smart contract for approvals
            contract_result = await call_smart_contract_settlement(
                request.policy_id,
                decision,
                settlement_amount
            )
            transaction_success = contract_result["success"]
            transaction_id = contract_result["transaction_id"]
            actual_payout = contract_result["payout_amount"]
        else:
            # For rejections, no transaction needed
            transaction_success = True
            actual_payout = 0

        # Use actual payout from contract if available, otherwise use expected
        final_settlement_amount = actual_payout if actual_payout > 0 else settlement_amount

        return OracleSettlementResponse(
            decision=decision,
            reasoning=analysis_data["reasoning"],
            reasoning_steps=analysis_data["reasoning_steps"],
            web_sources=analysis_data["web_sources"],
            confidence=analysis_data["confidence"],
            settlement_amount=final_settlement_amount,
            transaction_success=transaction_success,
            transaction_id=transaction_id
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Oracle settlement failed: {str(e)}")

@app.post("/set-oracle", response_model=SetOracleResponse)
async def set_oracle(request: SetOracleRequest):
    """Set the oracle account on the smart contract (admin only)"""
    try:
        # Set up Algorand client
        from algosdk.v2client import algod
        algod_client = algod.AlgodClient(ALGOD_TOKEN, f"{ALGOD_SERVER}:{ALGOD_PORT}")

        # For setting oracle, we need admin account (you might want to use a different approach)
        # For now, we'll use the oracle account as admin for simplicity
        oracle_private_key = mnemonic.to_private_key(ORACLE_MNEMONIC)
        oracle_address = account.address_from_private_key(oracle_private_key)

        print(f"🔑 Setting Oracle Address: {request.oracle_address}")

        # Create AlgoKit client
        algorand = AlgorandClient.from_clients(algod_client, algod_client)

        # Create app client
        from smart_contracts.artifacts.insurance.agri_guard_insurance_client import AgriGuardInsuranceClient, APP_SPEC

        app_client = algorand.application_client(
            app_id=int(APP_ID),
            app_spec=APP_SPEC,
            sender=oracle_address  # Using oracle as sender (should be admin)
        )

        # Set the signer
        algorand.set_default_signer(oracle_private_key)

        print(f"🔄 Calling set_oracle with address={request.oracle_address}")

        # Call the set_oracle method
        result = app_client.call(
            method="set_oracle",
            args={
                "oracle": request.oracle_address
            }
        )

        print(f"✅ Oracle set successfully! Transaction ID: {result.tx_id if hasattr(result, 'tx_id') else 'N/A'}")

        return SetOracleResponse(
            success=True,
            transaction_id=result.tx_id if hasattr(result, 'tx_id') else None,
            oracle_address=request.oracle_address
        )

    except Exception as e:
        print(f"❌ Failed to set oracle: {str(e)}")
        return SetOracleResponse(
            success=False,
            oracle_address=request.oracle_address,
            error=str(e)
        )

@app.get("/get-oracle")
async def get_oracle():
    """Get the current oracle account from the smart contract"""
    try:
        # Set up Algorand client
        from algosdk.v2client import algod
        algod_client = algod.AlgodClient(ALGOD_TOKEN, f"{ALGOD_SERVER}:{ALGOD_PORT}")

        # Create AlgoKit client
        algorand = AlgorandClient.from_clients(algod_client, algod_client)

        # Create app client (no sender needed for readonly call)
        from smart_contracts.artifacts.insurance.agri_guard_insurance_client import AgriGuardInsuranceClient, APP_SPEC

        app_client = algorand.application_client(
            app_id=int(APP_ID),
            app_spec=APP_SPEC
        )

        # Call the get_oracle method
        result = app_client.call(method="get_oracle")

        oracle_address = result.return_value if hasattr(result, 'return_value') else "Not set"

        return {
            "oracle_address": oracle_address,
            "success": True
        }

    except Exception as e:
        return {
            "oracle_address": "Error retrieving",
            "success": False,
            "error": str(e)
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)