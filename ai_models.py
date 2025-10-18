import random

def predict_best_yield():
    tokens = ["PENDLE", "ETH", "DAI", "USDC", "WBTC"]
    predicted = random.choice(tokens)
    expected_yield = round(random.uniform(3, 12), 2)
    return {"predicted_best_token": predicted, "expected_yield": f"{expected_yield}%"}

def predict_future_yield(token: str, days: int = 3):
    base = random.uniform(3, 12)
    return [round(base + random.uniform(-0.5, 0.5), 2) for _ in range(days)]