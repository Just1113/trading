def calculate_trade_params(entry_price, action, balance, settings, pair="BTC/USDT"):
    risk = settings['risk_percent'] / 100
    tp_rr = settings['tp_rr']
    leverage = settings['leverage'].get(pair, 10)
    sl_percent = 0.01  # default 1% SL

    if action == "BUY":
        sl = entry_price * (1 - sl_percent)
        tp = entry_price + (entry_price - sl) * tp_rr
    else:
        sl = entry_price * (1 + sl_percent)
        tp = entry_price - (sl - entry_price) * tp_rr

    position_size = balance * risk / abs(entry_price - sl)
    return sl, tp, position_size, leverage
