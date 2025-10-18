import os
import sys
import requests
from typing import Dict, Any
from pydantic import BaseModel, Field
from fastmcp import FastMCP
app = FastAPI(title="Pendle FastMCP API")

@app.get("/")
def home():
    return {"message": "Pendle Finance MCP is running successfully 🚀"}
from dotenv import load_dotenv
from web3 import Web3
from eth_account import Account
from ai_models import predict_best_yield, predict_future_yield  # AI logic

# -------------------------------
# 1. LOAD ENVIRONMENT VARIABLES
# -------------------------------
load_dotenv()
RPC_URL = os.environ.get("RPC_URL")
PRIVATE_KEY = os.environ.get("PRIVATE_KEY")
PENDLE_API_URL = os.environ.get("PENDLE_API_URL", "https://api.pendle.finance/v1/yields")

# -------------------------------
# 2. WALLET / KEY VALIDATION
# -------------------------------
wallet_valid = True
user_address = "0x000000000000000000000000000000000000DEAD"
w3 = Web3(Web3.HTTPProvider(RPC_URL)) if RPC_URL else None
account = None

if not PRIVATE_KEY:
    wallet_valid = False
    print("WARNING: PRIVATE_KEY not set. Blockchain tools disabled.", file=sys.stderr)
else:
    try:
        key_bytes = PRIVATE_KEY.lower().replace("0x", "")
        account = Account.from_key(key_bytes)
        user_address = account.address
    except Exception as e:
        wallet_valid = False
        print(f"ERROR: Invalid private key: {e}", file=sys.stderr)

# -------------------------------
# 3. INITIALIZE FASTMCP SERVER
# -------------------------------
mcp = FastMCP(
    name="Pendle Finance MCP",
    instructions="Provides Pendle market data, staking simulation, and AI yield predictions."
)

# -------------------------------
# 4. PENDLE TOOLS
# -------------------------------

# --- Transaction Model ---
class Transaction(BaseModel):
    user_address: str = Field(..., description="User wallet address")
    token: str = Field(..., description="Token symbol (e.g., PENDLE, ETH)")
    amount: float = Field(..., gt=0, description="Amount to stake or swap")

# --- Get top yields ---
@mcp.tool()
async def get_yield() -> Dict[str, Any]:
    try:
        res = requests.get(PENDLE_API_URL, timeout=5).json()
        top5 = res[:5] if isinstance(res, list) else []
        print(f"[INFO] Fetched top yields: {top5}", file=sys.stderr)
        return {"top_yields": top5}
    except Exception as e:
        print(f"[ERROR] Failed to fetch yields: {e}", file=sys.stderr)
        return {"error": f"Failed to fetch yields: {str(e)}"}

# --- Simulate staking ---
@mcp.tool()
async def stake(data: Transaction) -> Dict[str, Any]:
    print(f"[INFO] Staking simulation: {data.amount} {data.token} for {data.user_address}", file=sys.stderr)
    # Mock transaction hash
    tx_hash = f"0x{'{:064x}'.format(hash(data.user_address + data.token) % (10**64))}"
    return {"status": "success", "message": f"Simulated staking {data.amount} {data.token}", "tx_hash": tx_hash}

# --- Simulate swapping ---
@mcp.tool()
async def swap(data: Transaction) -> Dict[str, Any]:
    print(f"[INFO] Swap simulation: {data.amount} {data.token} for {data.user_address}", file=sys.stderr)
    tx_hash = f"0x{'{:064x}'.format(hash(data.token + str(data.amount)) % (10**64))}"
    return {"status": "success", "tx_hash": tx_hash}

# --- Portfolio ---
@mcp.tool()
async def portfolio(address: str) -> Dict[str, Any]:
    print(f"[INFO] Fetching portfolio for {address}", file=sys.stderr)
    holdings = [
        {"token": "PENDLE", "amount": 200},
        {"token": "ETH", "amount": 0.5}
    ]
    return {"address": address, "holdings": holdings, "yield": "5.4%"}

# -------------------------------
# 5. AI PREDICTION TOOLS
# -------------------------------

@mcp.tool()
async def predict_best_token() -> Dict[str, Any]:
    try:
        result = predict_best_yield()
        print(f"[INFO] AI Best Token Prediction: {result}", file=sys.stderr)
        return result
    except Exception as e:
        print(f"[ERROR] AI prediction failed: {e}", file=sys.stderr)
        return {"error": f"AI prediction failed: {str(e)}"}

@mcp.tool()
async def predict_future(token: str, days: int = 3) -> Dict[str, Any]:
    try:
        result = predict_future_yield(token, days)
        print(f"[INFO] AI Future Yield Prediction for {token}: {result}", file=sys.stderr)
        return {"token": token, "predictions": result}
    except Exception as e:
        print(f"[ERROR] Future prediction failed: {e}", file=sys.stderr)
        return {"error": f"Future prediction failed: {str(e)}"}

# -------------------------------
# 6. UTILITY / DEBUG TOOLS
# -------------------------------

@mcp.tool()
async def server_status() -> Dict[str, Any]:
    return {
        "status": "running",
        "user_address": user_address,
        "wallet_connected": wallet_valid,
        "pendle_api": PENDLE_API_URL
    }

# -------------------------------
# 7. RUN SERVER
# -------------------------------
if __name__ == "__main__":
    print(f"Starting Pendle MCP Server for address: {user_address}", file=sys.stderr)
    mcp.run()
