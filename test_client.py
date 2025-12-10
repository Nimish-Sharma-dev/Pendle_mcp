"""
Pendle MCP Server - Validation and Testing Guide

IMPORTANT: This server uses the Model Context Protocol (MCP) with stdio transport,
NOT a REST API. You cannot test it with HTTP requests or the requests library.

=============================================================================
HOW TO TEST THE SERVER
=============================================================================

Method 1: MCP Inspector (Recommended)
--------------------------------------
The MCP Inspector provides a web-based UI to test all MCP tools interactively.

1. Install Node.js (if not already installed)
2. Run the inspector:
   
   npx @modelcontextprotocol/inspector python server.py

3. Open the URL shown in your browser (usually http://localhost:6274)
4. In the "Tools" tab, you'll see all available tools
5. Click on any tool to test it with custom inputs

Method 2: Direct Server Execution
----------------------------------
Run the server directly to verify it starts without errors:

   python server.py

You should see startup logs confirming:
- Environment variables loaded
- Pendle API URL configured
- Wallet status (if configured)
- Server ready message

Press Ctrl+C to stop the server.

=============================================================================
AVAILABLE MCP TOOLS
=============================================================================

1. get_yield(limit: int = 10)
   - Fetches top yield opportunities from Pendle markets
   - Returns real-time APY data, liquidity, and protocol info
   - Example: {"limit": 5}

2. stake(data: Transaction)
   - Simulates staking tokens
   - Example: {
       "user_address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
       "token": "PENDLE",
       "amount": 100
     }

3. swap(data: Transaction)
   - Simulates token swaps
   - Example: {
       "user_address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
       "token": "sUSDe",
       "amount": 50
     }

4. portfolio(address: str)
   - Gets portfolio information for a wallet
   - Example: "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb"

5. predict_best_token()
   - AI-powered recommendation for best yield opportunity
   - No parameters needed
   - Uses weighted scoring: 40% APY, 30% liquidity, 20% underlying, 10% expiry

6. predict_future(token: str, days: int = 7)
   - Predicts future yield for a token over N days
   - Example: {"token": "sUSDe", "days": 7}

7. server_status()
   - Returns server health and configuration
   - No parameters needed

=============================================================================
VALIDATION SCRIPT
=============================================================================
"""

import sys
import os
from pathlib import Path

def validate_environment():
    """Validate environment configuration"""
    print("\n" + "="*70)
    print("PENDLE MCP SERVER - ENVIRONMENT VALIDATION")
    print("="*70 + "\n")
    
    # Check Python version
    print("[OK] Python Version:", sys.version.split()[0])
    
    # Check .env file
    env_path = Path(__file__).parent / ".env"
    if env_path.exists():
        print("[OK] .env file found")
    else:
        print("[!] .env file not found (optional)")
    
    # Check environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    pendle_api = os.getenv("PENDLE_API_URL", "Not set")
    rpc_url = os.getenv("RPC_URL", "Not set")
    private_key = os.getenv("PRIVATE_KEY", "Not set")
    
    print(f"[OK] PENDLE_API_URL: {pendle_api}")
    print(f"{'[OK]' if rpc_url != 'Not set' else '[!]'} RPC_URL: {'Configured' if rpc_url != 'Not set' else 'Not set (optional)'}")
    print(f"{'[OK]' if private_key != 'Not set' and private_key.strip() else '[!]'} PRIVATE_KEY: {'Configured' if private_key != 'Not set' and private_key.strip() else 'Not set (optional)'}")
    
    # Check dependencies
    print("\nChecking dependencies...")
    required_packages = [
        'fastmcp',
        'dotenv',
        'requests',
        'pydantic',
        'web3',
        'eth_account'
    ]
    
    missing = []
    for package in required_packages:
        try:
            if package == 'dotenv':
                __import__('dotenv')
            elif package == 'eth_account':
                __import__('eth_account')
            else:
                __import__(package)
            print(f"  [OK] {package}")
        except ImportError:
            print(f"  [X] {package} - MISSING")
            missing.append(package)
    
    if missing:
        print(f"\n[X] Missing packages: {', '.join(missing)}")
        print("  Run: pip install -r requirements.txt")
        return False
    
    # Test Pendle API connectivity
    print("\nTesting Pendle API connectivity...")
    try:
        import requests
        response = requests.get(
            "https://api-v2.pendle.finance/core/v1/1/markets",
            params={"limit": 1},
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            total = data.get('total', 0)
            print(f"  [OK] Pendle API connected ({total} markets available)")
        else:
            print(f"  [X] Pendle API returned HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"  [X] Pendle API connection failed: {e}")
        return False
    
    # Test server import
    print("\nTesting server import...")
    try:
        import server
        print("  [OK] server.py imports successfully")
    except Exception as e:
        print(f"  [X] server.py import failed: {e}")
        return False
    
    print("\n" + "="*70)
    print("[OK] ALL VALIDATION CHECKS PASSED")
    print("="*70)
    print("\nServer is ready to run!")
    print("\nTo start the server:")
    print("  python server.py")
    print("\nTo test with MCP Inspector:")
    print("  npx @modelcontextprotocol/inspector python server.py")
    print("\n" + "="*70 + "\n")
    
    return True


if __name__ == "__main__":
    print(__doc__)
    
    # Run validation
    try:
        success = validate_environment()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nValidation interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n[X] Validation failed with error: {e}")
        sys.exit(1)
