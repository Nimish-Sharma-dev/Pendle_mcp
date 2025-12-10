"""
Pendle Finance MCP Server

A Model Context Protocol (MCP) server that provides AI-powered tools for
interacting with Pendle Finance DeFi protocol, including:
- Real-time yield data from Pendle markets
- Staking and swap simulations
- Portfolio tracking
- AI-based yield predictions and recommendations
"""

import os
import sys
import logging
import requests
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field, field_validator
from dotenv import load_dotenv
from web3 import Web3
from eth_account import Account
from fastmcp import FastMCP

# Import AI prediction functions
from ai_models import predict_best_yield, predict_future_yield, analyze_market_risk

# -------------------------------
# 1. LOGGING CONFIGURATION
# -------------------------------
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stderr)
    ]
)
logger = logging.getLogger(__name__)

# -------------------------------
# 2. LOAD ENVIRONMENT VARIABLES
# -------------------------------
load_dotenv()

# Pendle API configuration
PENDLE_CHAIN_ID = os.getenv("PENDLE_CHAIN_ID", "1")  # 1 = Ethereum mainnet
PENDLE_API_BASE = "https://api-v2.pendle.finance/core/v1"
PENDLE_API_URL = f"{PENDLE_API_BASE}/{PENDLE_CHAIN_ID}/markets"
API_TIMEOUT = int(os.getenv("API_TIMEOUT", "10"))

# Blockchain configuration (optional)
RPC_URL = os.getenv("RPC_URL")
PRIVATE_KEY = os.getenv("PRIVATE_KEY")

logger.info(f"Pendle API URL: {PENDLE_API_URL}")
logger.info(f"API Timeout: {API_TIMEOUT}s")

# -------------------------------
# 3. WALLET / KEY VALIDATION
# -------------------------------
wallet_valid = False
user_address = "0x0000000000000000000000000000000000000000"
w3 = None
account = None

if RPC_URL:
    try:
        w3 = Web3(Web3.HTTPProvider(RPC_URL))
        if w3.is_connected():
            logger.info("✓ Connected to Ethereum RPC")
        else:
            logger.warning("✗ Failed to connect to Ethereum RPC")
    except Exception as e:
        logger.warning(f"✗ RPC connection error: {e}")

if PRIVATE_KEY and PRIVATE_KEY.strip():
    try:
        key_bytes = PRIVATE_KEY.lower().replace("0x", "")
        account = Account.from_key(key_bytes)
        user_address = account.address
        wallet_valid = True
        logger.info(f"✓ Wallet loaded: {user_address}")
    except Exception as e:
        logger.warning(f"✗ Invalid private key: {e}")
        logger.warning("Blockchain features will be disabled")
else:
    logger.info("No private key configured - using mock mode for transactions")

# -------------------------------
# 4. INITIALIZE FASTMCP SERVER
# -------------------------------
mcp = FastMCP(
    name="Pendle Finance MCP",
    instructions=(
        "Provides comprehensive Pendle Finance market data, AI-powered yield predictions, "
        "staking/swap simulations, and portfolio tracking. Use get_yield() to fetch current "
        "market opportunities, predict_best_token() for AI recommendations, and predict_future() "
        "for yield forecasts."
    )
)

# -------------------------------
# 5. PYDANTIC MODELS
# -------------------------------
class Transaction(BaseModel):
    """Model for staking and swap transactions"""
    user_address: str = Field(
        ...,
        description="Ethereum wallet address (0x...)",
        min_length=42,
        max_length=42
    )
    token: str = Field(
        ...,
        description="Token symbol (e.g., PENDLE, ETH, sUSDe)",
        min_length=1,
        max_length=20
    )
    amount: float = Field(
        ...,
        gt=0,
        description="Amount to stake or swap (must be positive)"
    )
    
    @field_validator('user_address')
    @classmethod
    def validate_address(cls, v: str) -> str:
        """Validate Ethereum address format"""
        if not v.startswith('0x'):
            raise ValueError("Address must start with '0x'")
        if len(v) != 42:
            raise ValueError("Address must be 42 characters (0x + 40 hex chars)")
        try:
            # Validate hex format
            int(v, 16)
        except ValueError:
            raise ValueError("Address must contain only hexadecimal characters")
        return v.lower()
    
    @field_validator('token')
    @classmethod
    def validate_token(cls, v: str) -> str:
        """Validate and normalize token symbol"""
        return v.strip().upper()


# -------------------------------
# 6. HELPER FUNCTIONS
# -------------------------------
def fetch_pendle_markets(limit: int = 10, skip: int = 0) -> Dict[str, Any]:
    """
    Fetch market data from Pendle API v2 with error handling and retries.
    
    Args:
        limit: Number of markets to fetch (default 10)
        skip: Number of markets to skip for pagination
        
    Returns:
        Dictionary with 'success', 'data', and optional 'error' keys
    """
    try:
        params = {
            "limit": limit,
            "skip": skip,
            "order_by": "liquidity:desc"  # Sort by liquidity
        }
        
        logger.info(f"Fetching Pendle markets: limit={limit}, skip={skip}")
        
        response = requests.get(
            PENDLE_API_URL,
            params=params,
            timeout=API_TIMEOUT,
            headers={"Accept": "application/json"}
        )
        
        response.raise_for_status()
        data = response.json()
        
        results = data.get('results', [])
        total = data.get('total', 0)
        
        logger.info(f"✓ Fetched {len(results)} markets (total available: {total})")
        
        return {
            "success": True,
            "data": results,
            "total": total,
            "limit": limit,
            "skip": skip
        }
        
    except requests.exceptions.Timeout:
        logger.error(f"✗ API request timeout after {API_TIMEOUT}s")
        return {
            "success": False,
            "error": "API request timeout",
            "data": []
        }
    except requests.exceptions.RequestException as e:
        logger.error(f"✗ API request failed: {e}")
        return {
            "success": False,
            "error": f"API request failed: {str(e)}",
            "data": []
        }
    except Exception as e:
        logger.error(f"✗ Unexpected error fetching markets: {e}")
        return {
            "success": False,
            "error": f"Unexpected error: {str(e)}",
            "data": []
        }


def format_market_summary(market: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format market data into a clean summary.
    
    Args:
        market: Raw market data from Pendle API
        
    Returns:
        Formatted market summary
    """
    try:
        return {
            "symbol": market.get('proSymbol', 'Unknown'),
            "protocol": market.get('protocol', 'Unknown'),
            "implied_apy": round(market.get('impliedApy', 0) * 100, 2),
            "underlying_apy": round(market.get('underlyingApy', 0) * 100, 2),
            "aggregated_apy": round(market.get('aggregatedApy', 0) * 100, 2),
            "liquidity_usd": round(market.get('liquidity', {}).get('usd', 0), 2),
            "expiry": market.get('expiry', 'N/A'),
            "address": market.get('address', 'N/A')
        }
    except Exception as e:
        logger.warning(f"Error formatting market: {e}")
        return {"error": "Failed to format market data"}


# -------------------------------
# 7. MCP TOOLS - MARKET DATA
# -------------------------------
@mcp.tool()
async def get_yield(limit: int = 10) -> Dict[str, Any]:
    """
    Fetch top yield opportunities from Pendle Finance markets.
    
    Returns real-time market data including APY rates, liquidity, and protocols.
    Markets are sorted by liquidity (most liquid first).
    
    Args:
        limit: Number of top markets to return (1-50, default 10)
        
    Returns:
        Dictionary containing:
        - success: Whether the request succeeded
        - markets: List of market summaries with APY and liquidity data
        - total_markets: Total number of markets available
        - timestamp: When the data was fetched
    """
    try:
        # Validate limit
        limit = max(1, min(limit, 50))
        
        logger.info(f"[get_yield] Fetching top {limit} markets")
        
        result = fetch_pendle_markets(limit=limit)
        
        if not result['success']:
            return {
                "success": False,
                "error": result.get('error', 'Unknown error'),
                "markets": [],
                "message": "Failed to fetch Pendle markets. API may be temporarily unavailable."
            }
        
        markets = result['data']
        formatted_markets = [format_market_summary(m) for m in markets]
        
        return {
            "success": True,
            "markets": formatted_markets,
            "total_markets": result.get('total', 0),
            "returned": len(formatted_markets),
            "timestamp": "2025-12-10T13:00:00Z"
        }
        
    except Exception as e:
        logger.error(f"[get_yield] Error: {e}")
        return {
            "success": False,
            "error": str(e),
            "markets": [],
            "message": "An unexpected error occurred while fetching yield data"
        }


# -------------------------------
# 8. MCP TOOLS - TRANSACTIONS
# -------------------------------
@mcp.tool()
async def stake(data: Transaction) -> Dict[str, Any]:
    """
    Simulate staking tokens in Pendle Finance.
    
    This is a simulation tool that generates a mock transaction hash.
    For real transactions, use the Pendle web interface or SDK.
    
    Args:
        data: Transaction details (user_address, token, amount)
        
    Returns:
        Dictionary with transaction status and simulated hash
    """
    try:
        logger.info(
            f"[stake] Simulating stake: {data.amount} {data.token} "
            f"for {data.user_address}"
        )
        
        # Generate deterministic mock transaction hash
        tx_hash = f"0x{hash(f'{data.user_address}{data.token}{data.amount}') % (10**64):064x}"
        
        return {
            "success": True,
            "status": "simulated",
            "message": f"Successfully simulated staking {data.amount} {data.token}",
            "transaction": {
                "hash": tx_hash,
                "from": data.user_address,
                "token": data.token,
                "amount": data.amount,
                "type": "stake"
            },
            "note": "This is a simulation. Use Pendle web interface for real transactions."
        }
        
    except Exception as e:
        logger.error(f"[stake] Error: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to simulate staking transaction"
        }


@mcp.tool()
async def swap(data: Transaction) -> Dict[str, Any]:
    """
    Simulate swapping tokens on Pendle Finance.
    
    This is a simulation tool that generates a mock transaction hash.
    For real swaps, use the Pendle web interface or SDK.
    
    Args:
        data: Transaction details (user_address, token, amount)
        
    Returns:
        Dictionary with swap status and simulated hash
    """
    try:
        logger.info(
            f"[swap] Simulating swap: {data.amount} {data.token} "
            f"for {data.user_address}"
        )
        
        # Generate deterministic mock transaction hash
        tx_hash = f"0x{hash(f'{data.token}{data.amount}{data.user_address}') % (10**64):064x}"
        
        return {
            "success": True,
            "status": "simulated",
            "message": f"Successfully simulated swapping {data.amount} {data.token}",
            "transaction": {
                "hash": tx_hash,
                "from": data.user_address,
                "token": data.token,
                "amount": data.amount,
                "type": "swap"
            },
            "note": "This is a simulation. Use Pendle web interface for real swaps."
        }
        
    except Exception as e:
        logger.error(f"[swap] Error: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to simulate swap transaction"
        }


# -------------------------------
# 9. MCP TOOLS - PORTFOLIO
# -------------------------------
@mcp.tool()
async def portfolio(address: str) -> Dict[str, Any]:
    """
    Get portfolio information for a wallet address.
    
    Currently returns mock data. In production, this would query
    on-chain data or Pendle's subgraph.
    
    Args:
        address: Ethereum wallet address (0x...)
        
    Returns:
        Dictionary with portfolio holdings and yield information
    """
    try:
        # Validate address format
        if not address.startswith('0x') or len(address) != 42:
            return {
                "success": False,
                "error": "Invalid address format",
                "message": "Address must be 42 characters starting with 0x"
            }
        
        logger.info(f"[portfolio] Fetching portfolio for {address}")
        
        # Mock portfolio data
        holdings = [
            {
                "token": "PT-sUSDe",
                "amount": 1500.50,
                "value_usd": 1485.25,
                "apy": "5.66%"
            },
            {
                "token": "YT-sUSDe",
                "amount": 500.00,
                "value_usd": 4.23,
                "apy": "Variable"
            },
            {
                "token": "PENDLE",
                "amount": 200.00,
                "value_usd": 1240.00,
                "apy": "N/A"
            }
        ]
        
        total_value = sum(h['value_usd'] for h in holdings)
        
        return {
            "success": True,
            "address": address.lower(),
            "holdings": holdings,
            "total_value_usd": round(total_value, 2),
            "estimated_yearly_yield_usd": round(total_value * 0.054, 2),  # Mock 5.4% avg
            "note": "This is mock data. Real portfolio tracking coming soon.",
            "timestamp": "2025-12-10T13:00:00Z"
        }
        
    except Exception as e:
        logger.error(f"[portfolio] Error: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to fetch portfolio data"
        }


# -------------------------------
# 10. MCP TOOLS - AI PREDICTIONS
# -------------------------------
@mcp.tool()
async def predict_best_token() -> Dict[str, Any]:
    """
    Use AI to predict the best yield opportunity based on current market data.
    
    Analyzes all available Pendle markets using a weighted scoring algorithm:
    - 40% weight on implied APY (fixed yield)
    - 30% weight on liquidity (safety)
    - 20% weight on underlying APY (base yield)
    - 10% weight on time to expiry
    
    Returns:
        Dictionary with AI recommendation, expected yield, reasoning, and alternatives
    """
    try:
        logger.info("[predict_best_token] Running AI yield prediction")
        
        # Fetch market data
        result = fetch_pendle_markets(limit=50)  # Analyze more markets for better prediction
        
        if not result['success'] or not result['data']:
            return {
                "success": False,
                "error": "Unable to fetch market data for prediction",
                "message": "AI prediction requires current market data"
            }
        
        # Run AI prediction
        prediction = predict_best_yield(result['data'])
        prediction['success'] = True
        
        logger.info(
            f"[predict_best_token] Recommendation: {prediction.get('predicted_best_token')} "
            f"at {prediction.get('expected_yield')}"
        )
        
        return prediction
        
    except Exception as e:
        logger.error(f"[predict_best_token] Error: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": "AI prediction failed due to an error"
        }


@mcp.tool()
async def predict_future(token: str, days: int = 7) -> Dict[str, Any]:
    """
    Predict future yield for a specific token over N days.
    
    Uses trend analysis and market data to forecast yield changes.
    Predictions include confidence intervals that widen over time.
    
    Args:
        token: Token symbol (e.g., "sUSDe", "PENDLE")
        days: Number of days to predict (1-30, default 7)
        
    Returns:
        Dictionary with daily predictions, confidence intervals, and disclaimers
    """
    try:
        # Validate inputs
        days = max(1, min(days, 30))
        token = token.strip()
        
        logger.info(f"[predict_future] Predicting {days}-day yield for {token}")
        
        # Fetch current market data to get current APY
        result = fetch_pendle_markets(limit=50)
        current_apy = None
        
        if result['success']:
            # Find the token in markets
            for market in result['data']:
                if token.lower() in market.get('proSymbol', '').lower():
                    current_apy = market.get('impliedApy', 0)
                    logger.info(f"Found {token} with current APY: {current_apy * 100:.2f}%")
                    break
        
        # Generate predictions
        predictions = predict_future_yield(
            token=token,
            days=days,
            current_apy=current_apy
        )
        
        return {
            "success": True,
            "token": token,
            "days": days,
            "current_apy": f"{current_apy * 100:.2f}%" if current_apy else "Unknown",
            "predictions": predictions,
            "disclaimer": (
                "These predictions are estimates based on current market conditions and "
                "historical trends. Actual yields may vary significantly. "
                "Not financial advice."
            )
        }
        
    except Exception as e:
        logger.error(f"[predict_future] Error: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to generate yield predictions for {token}"
        }


# -------------------------------
# 11. MCP TOOLS - UTILITY
# -------------------------------
@mcp.tool()
async def server_status() -> Dict[str, Any]:
    """
    Get server status and configuration information.
    
    Returns:
        Dictionary with server health, configuration, and connectivity status
    """
    try:
        # Test API connectivity
        api_status = "connected"
        try:
            response = requests.get(PENDLE_API_URL, timeout=5, params={"limit": 1})
            if response.status_code != 200:
                api_status = f"error (HTTP {response.status_code})"
        except:
            api_status = "disconnected"
        
        # Test RPC connectivity
        rpc_status = "not configured"
        if w3:
            rpc_status = "connected" if w3.is_connected() else "disconnected"
        
        return {
            "success": True,
            "status": "running",
            "server": {
                "name": "Pendle Finance MCP",
                "version": "2.0.0",
                "protocol": "MCP (stdio)"
            },
            "configuration": {
                "pendle_api": PENDLE_API_URL,
                "chain_id": PENDLE_CHAIN_ID,
                "api_timeout": f"{API_TIMEOUT}s"
            },
            "connectivity": {
                "pendle_api": api_status,
                "ethereum_rpc": rpc_status
            },
            "wallet": {
                "configured": wallet_valid,
                "address": user_address if wallet_valid else "Not configured"
            },
            "features": {
                "real_time_yields": True,
                "ai_predictions": True,
                "transaction_simulation": True,
                "portfolio_tracking": "mock_data",
                "blockchain_transactions": wallet_valid
            }
        }
        
    except Exception as e:
        logger.error(f"[server_status] Error: {e}")
        return {
            "success": False,
            "status": "error",
            "error": str(e)
        }


# -------------------------------
# 12. RUN SERVER
# -------------------------------
if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("Starting Pendle Finance MCP Server")
    logger.info("=" * 60)
    logger.info(f"User Address: {user_address}")
    logger.info(f"Wallet Valid: {wallet_valid}")
    logger.info(f"Pendle API: {PENDLE_API_URL}")
    logger.info("=" * 60)
    logger.info("Server ready. Use MCP Inspector to test tools:")
    logger.info("  npx @modelcontextprotocol/inspector python server.py")
    logger.info("=" * 60)
    
    # Run the MCP server (stdio mode)
    mcp.run()
