"""
Quick Pendle AI Recommendation Script

This script fetches real-time Pendle market data and uses AI to recommend
the best yield opportunity.
"""

from ai_models import predict_best_yield
import requests


def get_ai_recommendation():
    """Fetch markets and get AI recommendation"""
    
    print("=" * 70)
    print("PENDLE AI YIELD RECOMMENDATION")
    print("=" * 70)
    print()
    
    # Fetch markets from Pendle API
    print("Fetching market data from Pendle Finance...")
    try:
        response = requests.get(
            "https://api-v2.pendle.finance/core/v1/1/markets",
            params={"limit": 50, "order_by": "liquidity:desc"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            markets = data.get('results', [])
            total = data.get('total', 0)
            
            print(f"[OK] Fetched {len(markets)} markets (out of {total} total)")
            print()
            
            # Get AI recommendation
            print("Running AI analysis...")
            prediction = predict_best_yield(markets)
            
            print()
            print("=" * 70)
            print("AI RECOMMENDATION")
            print("=" * 70)
            print()
            print(f"Best Token: {prediction.get('predicted_best_token')}")
            print(f"Protocol: {prediction.get('protocol')}")
            print(f"Expected Yield: {prediction.get('expected_yield')}")
            print(f"Underlying Yield: {prediction.get('underlying_yield')}")
            print(f"Liquidity: ${prediction.get('liquidity_usd'):,.0f}")
            print(f"Days to Expiry: {prediction.get('days_to_expiry')}")
            print(f"Confidence: {prediction.get('confidence').upper()}")
            print()
            print("Reasoning:")
            print(f"  {prediction.get('reasoning')}")
            print()
            
            # Show alternatives
            if prediction.get('top_3_alternatives'):
                print("Top 3 Alternatives:")
                print("-" * 70)
                for i, alt in enumerate(prediction.get('top_3_alternatives', []), 1):
                    print(f"  {i}. {alt.get('symbol')} - {alt.get('apy')} on {alt.get('protocol')}")
                print()
            
            print("=" * 70)
            print()
            
            return prediction
            
        else:
            print(f"[X] API Error: Status code {response.status_code}")
            print("    This might be due to rate limiting. Try again in a moment.")
            return None
            
    except Exception as e:
        print(f"[X] Error: {e}")
        return None


if __name__ == "__main__":
    print()
    result = get_ai_recommendation()
    
    if result:
        print("Tip: You can use this data to make informed DeFi investment decisions!")
    else:
        print("Tip: If you see a rate limit error, wait a few seconds and try again.")
    print()
