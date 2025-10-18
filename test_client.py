import requests

BASE = "http://127.0.0.1:8000"

print(requests.get(f"{BASE}/get_yield").json())
print(requests.post(f"{BASE}/stake", json={"user_address":"0x123", "token":"PENDLE", "amount":10}).json())