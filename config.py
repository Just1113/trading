import os

# Telegram
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "123456789"))

# Bybit API
BYBIT_API_KEY = os.getenv("BYBIT_API_KEY")
BYBIT_API_SECRET = os.getenv("BYBIT_API_SECRET")

# Admin settings
ADMIN_SETTINGS = {
    'leverage': {'BTC/USDT': 10, 'ETH/USDT': 10},
    'risk_percent': 2,      # % of balance per trade
    'tp_rr': 2,             # Take-profit R/R ratio
    'ml_threshold': 70      # Minimum ML prediction %
}
