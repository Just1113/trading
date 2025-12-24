import requests
import time
import os
import hmac
import hashlib

BASE_URL = "https://api.bybitglobal.com"

API_KEY = os.environ.get("BYBIT_API_KEY")
API_SECRET = os.environ.get("BYBIT_API_SECRET")

def _sign(params):
    query = "&".join([f"{k}={v}" for k, v in sorted(params.items())])
    return hmac.new(
        API_SECRET.encode(),
        query.encode(),
        hashlib.sha256
    ).hexdigest()

def get_wallet_balance():
    timestamp = int(time.time() * 1000)
    params = {
        "api_key": API_KEY,
        "timestamp": timestamp,
        "accountType": "UNIFIED"
    }
    params["sign"] = _sign(params)

    r = requests.get(f"{BASE_URL}/v5/account/wallet-balance", params=params, timeout=10)
    r.raise_for_status()
    return r.json()
