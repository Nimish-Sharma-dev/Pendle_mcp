"""
Test client for Pendle MCP Server

Note: This server uses FastMCP protocol, not REST API.
To test it properly, use the MCP Inspector:
    npx @modelcontextprotocol/inspector

Or run the server directly:
    python server.py

The server exposes these MCP tools:
- get_yield() - Fetch top yields from Pendle
- stake(data) - Simulate staking
- swap(data) - Simulate swap
- portfolio(address) - Get portfolio
- predict_best_token() - AI token prediction
- predict_future(token, days) - AI yield prediction
- server_status() - Server status
"""

if __name__ == "__main__":
    print(__doc__)
    print("\nTo test the server, run:")
    print("  python server.py")
    print("\nOr use MCP Inspector:")
    print("  npx @modelcontextprotocol/inspector")
