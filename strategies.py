import pandas as pd
from ta.trend import EMAIndicator, MACD
from ta.momentum import RSIIndicator
from ta.volatility import BollingerBands
import numpy as np

# ------------------------
# Strategy Modules
# ------------------------
def ema_crossover(df):
    df['ema_short'] = EMAIndicator(df['close'], 9).ema_indicator()
    df['ema_long'] = EMAIndicator(df['close'], 21).ema_indicator()
    if df['ema_short'].iloc[-1] > df['ema_long'].iloc[-1] and df['ema_short'].iloc[-2] <= df['ema_long'].iloc[-2]:
        return 'BUY', 80
    elif df['ema_short'].iloc[-1] < df['ema_long'].iloc[-1] and df['ema_short'].iloc[-2] >= df['ema_long'].iloc[-2]:
        return 'SELL', 80
    return None, 0

def rsi_strategy(df):
    rsi = RSIIndicator(df['close'], 14).rsi()
    if rsi.iloc[-1] < 30:
        return 'BUY', 70
    elif rsi.iloc[-1] > 70:
        return 'SELL', 70
    return None, 0

def bollinger_strategy(df):
    bb = BollingerBands(df['close'], 20, 2)
    if df['close'].iloc[-1] < bb.bollinger_lband().iloc[-1]:
        return 'BUY', 65
    elif df['close'].iloc[-1] > bb.bollinger_hband().iloc[-1]:
        return 'SELL', 65
    return None, 0

def macd_strategy(df):
    macd = MACD(df['close'])
    if macd.macd_diff().iloc[-1] > 0 and macd.macd_diff().iloc[-2] <= 0:
        return 'BUY', 75
    elif macd.macd_diff().iloc[-1] < 0 and macd.macd_diff().iloc[-2] >= 0:
        return 'SELL', 75
    return None, 0

def breakout_strategy(df):
    recent_high = df['high'].iloc[-20:].max()
    recent_low = df['low'].iloc[-20:].min()
    if df['close'].iloc[-1] > recent_high:
        return 'BUY', 70
    elif df['close'].iloc[-1] < recent_low:
        return 'SELL', 70
    return None, 0

# ------------------------
# Aggregator
# ------------------------
def aggregate_strategies(df):
    strategies = [ema_crossover, rsi_strategy, bollinger_strategy, macd_strategy, breakout_strategy]
    actions = []
    triggered = []
    total_conf = []

    for strat in strategies:
        action, conf = strat(df)
        if action:
            actions.append(action)
            triggered.append(strat.__name__)
            total_conf.append(conf)

    if not actions:
        return None, 0, []

    final_action = max(set(actions), key=actions.count)
    avg_conf = int(np.mean(total_conf))
    return final_action, avg_conf, triggered
