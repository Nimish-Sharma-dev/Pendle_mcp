# Alternative Ways to Run Pendle MCP Server

Your Pendle MCP server is fully functional! Here are **3 different ways** to use it:

## ✅ Method 1: Direct Python Testing (Easiest!)

Test all tools directly without any MCP client:

```bash
python test_tools.py
```

This will:
- ✓ Test all 7 tools automatically
- ✓ Show real Pendle market data
- ✓ Display AI predictions
- ✓ Simulate transactions
- ✓ No MCP Inspector needed!

### Interactive Mode

```bash
python test_tools.py --interactive
```

Choose which tool to test interactively.

---

## ✅ Method 2: Python Script Integration

Use the tools in your own Python scripts:

```python
import asyncio
from server import get_yield, predict_best_token

async def main():
    # Get top 5 yields
    yields = await get_yield(5)
    print(f"Top markets: {yields}")
    
    # Get AI recommendation
    prediction = await predict_best_token()
    print(f"Best token: {prediction}")

asyncio.run(main())
```

---

## ✅ Method 3: Build a Simple Web Interface

I can create a Flask/FastAPI web interface if you want a browser-based UI!

Would you like me to create:
- A simple web dashboard to view yields?
- A REST API wrapper around the MCP tools?
- A Streamlit dashboard for interactive exploration?

---

## ✅ Method 4: Claude Desktop (When It Works)

Once Claude Desktop properly detects the MCP server, you can use it through Claude's chat interface.

**Configuration is already set up at:**
`C:\Users\Test\AppData\Roaming\Claude\claude_desktop_config.json`

---

## 🚀 Quick Start

**Right now, the easiest way:**

```bash
# Test everything
python test_tools.py

# Or interactive mode
python test_tools.py --interactive
```

This gives you full access to all features without needing MCP Inspector or Claude Desktop!

---

## 📊 What You Can Do

All 7 tools are available:

1. **get_yield** - Real-time Pendle market data (365 markets)
2. **predict_best_token** - AI recommendations with reasoning
3. **predict_future** - 7-day yield forecasts
4. **stake** - Simulate staking transactions
5. **swap** - Simulate token swaps
6. **portfolio** - View portfolio holdings
7. **server_status** - Health check

---

## 💡 Want More?

Let me know if you want:
- Web dashboard
- REST API
- Streamlit app
- Jupyter notebook examples
- Or any other interface!

The server works perfectly - we just need the right interface for you! 🎉
