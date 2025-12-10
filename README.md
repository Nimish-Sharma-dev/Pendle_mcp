# Pendle Finance MCP Server 🚀

![Python](https://img.shields.io/badge/python-3.10+-blue)
![FastMCP](https://img.shields.io/badge/FastMCP-v0.2.0+-green)
![Pendle API](https://img.shields.io/badge/Pendle%20API-v2-orange)

A **Model Context Protocol (MCP) Server** for [Pendle Finance](https://www.pendle.finance/) that provides AI-powered tools for yield optimization, market analysis, and DeFi portfolio management.

## ✨ Features

- 🔍 **Real-time Market Data** - Fetch live yields from Pendle Finance markets
- 🤖 **AI Yield Predictions** - Smart recommendations using weighted scoring algorithm
- 📊 **Portfolio Tracking** - Monitor your DeFi holdings and yields
- 💱 **Transaction Simulation** - Test staking and swaps before executing
- 📈 **Future Yield Forecasts** - Predict yield trends over time
- 🛡️ **Risk Analysis** - Assess market risks based on liquidity and volatility

## 🎯 What is MCP?

The **Model Context Protocol (MCP)** is a standard for connecting AI assistants to external tools and data sources. This server exposes Pendle Finance functionality as MCP tools that can be used by AI agents like Claude, ChatGPT, or custom LLM applications.

**Important**: This is **NOT a REST API**. It uses stdio transport and must be tested with MCP-compatible tools.

## ⚙️ Setup and Installation

### 1. Prerequisites

- **Python 3.10+** installed on your system
- **Node.js 16+** (for MCP Inspector testing)
- **Git** (to clone the repository)

### 2. Clone the Repository

```bash
git clone https://github.com/maneesa029/Pendle_mcp
cd Pendle_mcp
```

### 3. Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate

# macOS/Linux:
source venv/bin/activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure Environment

The `.env` file is already configured with sensible defaults. You can customize it if needed:

```env
# Pendle API Configuration
PENDLE_API_URL=https://api-v2.pendle.finance/core/v1/1/markets
PENDLE_CHAIN_ID=1
API_TIMEOUT=10
LOG_LEVEL=INFO

# Optional: Blockchain Configuration (for real transactions)
RPC_URL=
PRIVATE_KEY=
```

⚠️ **Security Warning**: Never use your main wallet private key. For testing, leave `PRIVATE_KEY` empty to run in simulation-only mode.

## 🚀 Running the Server

### Method 1: Direct Execution

```bash
python server.py
```

You should see:
```
============================================================
Starting Pendle Finance MCP Server
============================================================
User Address: 0x0000000000000000000000000000000000000000
Wallet Valid: False
Pendle API: https://api-v2.pendle.finance/core/v1/1/markets
============================================================
Server ready. Use MCP Inspector to test tools:
  npx @modelcontextprotocol/inspector python server.py
============================================================
```

Press `Ctrl+C` to stop.

### Method 2: MCP Inspector (Recommended for Testing)

The MCP Inspector provides a web UI to test all tools interactively:

```bash
npx @modelcontextprotocol/inspector python server.py
```

This will:
1. Start the MCP server
2. Launch a web interface (usually at `http://localhost:6274`)
3. Open your browser automatically

In the Inspector:
- Go to the **Tools** tab
- See all 7 available tools
- Click any tool to test it with custom inputs
- View responses in real-time

## 🔧 Available MCP Tools

### 1. `get_yield(limit: int = 10)`
Fetch top yield opportunities from Pendle markets.

**Example Input:**
```json
{"limit": 5}
```

**Returns:** List of markets with APY, liquidity, protocol, and expiry data.

---

### 2. `stake(data: Transaction)`
Simulate staking tokens in Pendle Finance.

**Example Input:**
```json
{
  "user_address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
  "token": "PENDLE",
  "amount": 100
}
```

**Returns:** Simulated transaction hash and details.

---

### 3. `swap(data: Transaction)`
Simulate swapping tokens on Pendle.

**Example Input:**
```json
{
  "user_address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
  "token": "sUSDe",
  "amount": 50
}
```

**Returns:** Simulated swap transaction.

---

### 4. `portfolio(address: str)`
Get portfolio information for a wallet address.

**Example Input:**
```json
"0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb"
```

**Returns:** Holdings, total value, and estimated yields.

---

### 5. `predict_best_token()`
AI-powered recommendation for the best yield opportunity.

**No parameters needed.**

**Algorithm:**
- 40% weight on implied APY (fixed yield)
- 30% weight on liquidity (safety)
- 20% weight on underlying APY (base yield)
- 10% weight on time to expiry

**Returns:** Best token, expected yield, reasoning, and top 3 alternatives.

---

### 6. `predict_future(token: str, days: int = 7)`
Predict future yield for a token over N days.

**Example Input:**
```json
{
  "token": "sUSDe",
  "days": 7
}
```

**Returns:** Daily predictions with confidence intervals.

---

### 7. `server_status()`
Get server health and configuration.

**No parameters needed.**

**Returns:** Server status, API connectivity, wallet info, and feature availability.

## ✅ Validation & Testing

Run the validation script to check your setup:

```bash
python test_client.py
```

This will verify:
- ✓ Python version
- ✓ Environment configuration
- ✓ Dependencies installed
- ✓ Pendle API connectivity
- ✓ Server imports successfully

## 🐛 Troubleshooting

### Issue: "Module 'fastmcp' not found"
**Solution:**
```bash
pip install -r requirements.txt
```

### Issue: "Pendle API connection failed"
**Solution:**
- Check your internet connection
- Verify the API URL in `.env` is correct
- Try increasing `API_TIMEOUT` in `.env`

### Issue: "Server starts but no tools visible in Inspector"
**Solution:**
- Make sure you're using the correct command:
  ```bash
  npx @modelcontextprotocol/inspector python server.py
  ```
- Check that `server.py` has no syntax errors
- Look for error messages in the terminal

### Issue: "Invalid address format" when testing stake/swap
**Solution:**
- Addresses must be 42 characters (0x + 40 hex chars)
- Example valid address: `0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb`

### Issue: "Cannot test with requests library"
**Solution:**
- This is NOT a REST API - it uses MCP protocol (stdio)
- Use MCP Inspector instead: `npx @modelcontextprotocol/inspector python server.py`

## 📚 Project Structure

```
Pendle_mcp/
├── server.py           # Main MCP server with all tools
├── ai_models.py        # AI prediction algorithms
├── test_client.py      # Validation and testing script
├── requirements.txt    # Python dependencies
├── .env               # Configuration (API URLs, timeouts)
├── .gitignore         # Git ignore rules
├── README.md          # This file
└── setup.sh           # Quick setup script (Unix/Mac)
```

## 🔐 Security Best Practices

1. **Never commit `.env` with real private keys** to version control
2. **Never use your main wallet** - create a test wallet for development
3. **Use environment variables** in production, not `.env` files
4. **Validate all inputs** - the server includes Pydantic validation
5. **Monitor API usage** - respect Pendle API rate limits

## 🚧 Roadmap

- [ ] Real portfolio tracking via on-chain data
- [ ] Historical yield data and charts
- [ ] Multi-chain support (Arbitrum, Optimism)
- [ ] Advanced ML models for predictions
- [ ] Real blockchain transaction execution
- [ ] WebSocket support for live updates

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

- [Pendle Finance](https://www.pendle.finance/) for the amazing DeFi protocol
- [FastMCP](https://github.com/jlowin/fastmcp) for the MCP server framework
- [Model Context Protocol](https://modelcontextprotocol.io/) specification

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/maneesa029/Pendle_mcp/issues)
- **Pendle Docs**: [docs.pendle.finance](https://docs.pendle.finance/)
- **MCP Docs**: [modelcontextprotocol.io](https://modelcontextprotocol.io/)

---

**Built with ❤️ for the DeFi community**
