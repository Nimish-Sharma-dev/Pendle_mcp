Pendle Finance FastMCP Server 🚀

![Python](https://img.shields.io/badge/python-3.10+-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-v0.100.0-green)

This repository contains a *Model Context Protocol (MCP) Server* built with *FastMCP* in Python.  
It connects to *Pendle Finance* DeFi Protocol and exposes endpoints for AI agents or clients like *MCP Inspector*.

Features include:
- Fetching live yields from Pendle API
- Simulating staking and swaps
- Retrieving user DeFi portfolio
- AI-based token recommendations (simulated)
- AI future yield predictions (simulated)


⚙ Setup and Installation

1. Prerequisites

Python 3.10+ installed on your system

Node.js 16+ if you want to use MCP Inspector


2. Clone This Repo

git clone https://github.com/maneesa029/Pendle_mcp
cd Pendle_mcp

3. Create and Activate a Virtual Environment

# Create virtual environment
python -m venv venv

# Windows
.\venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

4. Install Dependencies

pip install -r requirements.txt

5. Configure .env

Create a .env file in the root folder and add your configuration:

# FastAPI settings
FASTAPI_ENV=development
HOST=127.0.0.1
PORT=8000

# Pendle API (no secret key needed for public endpoints)
PENDLE_API_URL=https://api.pendle.finance/v1/yields

# Ethereum testnet (if using staking simulation or swaps)
RPC_URL=https://sepolia.infura.io/v3/YOUR_INFURA_KEY
PRIVATE_KEY=0xYOUR_TEST_PRIVATE_KEY

⚠ Security Warning:
Do NOT use your main wallet private key with real funds. Always use a testnet key or a small segregated account for testing.


---

🔬 Running and Monitoring the Server

1. Start the Pendle MCP Server

uvicorn server:app --reload --port 8000

You should see:

INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.

2. Open MCP Inspector (Optional)

If you want to test tools interactively:

npx @modelcontextprotocol/inspector

This will launch a local URL (e.g., http://127.0.0.1:6274)

Open the URL in your browser

In Tools tab, you’ll see all exposed Pendle MCP functions:

get_yield → fetch top yields

stake → simulate staking

swap → simulate swap

portfolio → user portfolio

predict_best_token → AI-recommended token

predict_future → future yield prediction




---

✅ 3. Test via Python Client

# test_client.py
import requests

BASE = "http://127.0.0.1:8000"

print(requests.get(f"{BASE}/get_yield").json())
print(requests.post(f"{BASE}/stake", json={"user_address":"0x123","token":"PENDLE","amount":10}).json())
print(requests.get(f"{BASE}/predict_best_token").json())


---

🔹 Features

Fetch live Pendle yields from API

Simulate staking and swaps

Retrieve user DeFi portfolio

AI predicts best token to stake

AI predicts future yields for N days

Works seamlessly with MCP Inspector or any AI agent



---

🔹 Optional AI Improvements

Replace random predictions with historical yield ML model (scikit-learn / Prophet)

Include portfolio optimization for multiple tokens

Connect Ethereum testnet to simulate real transactions
