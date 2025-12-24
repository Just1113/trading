import time
import ccxt
import pandas as pd
from telebot import TeleBot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import TELEGRAM_TOKEN, ADMIN_ID, BYBIT_API_KEY, BYBIT_API_SECRET, ADMIN_SETTINGS
from strategies import aggregate_strategies
from utils import calculate_trade_params

bot = TeleBot(TELEGRAM_TOKEN)
exchange = ccxt.bybit({
    'apiKey': BYBIT_API_KEY,
    'secret': BYBIT_API_SECRET,
    'enableRateLimit': True,
})
exchange.set_sandbox_mode(True)

TRADE_QUEUE = {}

def ml_predict(df, action, strategy_conf):
    return strategy_conf  # Placeholder

def execute_trade(pair, action, size, entry_price, sl, tp, leverage):
    try:
        # Set leverage
        exchange.private_linear_post_position_leverage_save({
            'symbol': pair.replace("/", ""),
            'buy_leverage': leverage,
            'sell_leverage': leverage
        })

        # Market order
        order = exchange.create_order(
            symbol=pair,
            type='market',
            side=action,
            amount=size
        )

        # SL order
        sl_order = exchange.create_order(
            symbol=pair,
            type='stop_market',
            side='SELL' if action == 'BUY' else 'BUY',
            amount=size,
            params={'stop_px': sl}
        )

        # TP order
        tp_order = exchange.create_order(
            symbol=pair,
            type='take_profit_market',
            side='SELL' if action == 'BUY' else 'BUY',
            amount=size,
            params={'stop_px': tp}
        )

        print(f"Market order: {order}")
        print(f"SL order: {sl_order}")
        print(f"TP order: {tp_order}")

    except Exception as e:
        print("Trade execution error:", e)

def send_confirmation(chat_id, pair, action, strategy_conf, ml_pred, sl, tp, size, leverage, triggered, entry_price):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("Yes", callback_data="YES"),
               InlineKeyboardButton("No", callback_data="NO"))

    message = f"""
Signal: {pair} {action}
Triggered by: {', '.join(triggered)}
Strategy Confidence: {strategy_conf}%
ML Prediction: {ml_pred}%
Entry Price: {entry_price:.2f}
Stop-Loss: {sl:.2f}
Take-Profit: {tp:.2f}
Position Size: {size:.6f} {pair.split('/')[0]}
Leverage: {leverage}x
Take trade automatically?
"""
    msg = bot.send_message(chat_id, message, reply_markup=markup)
    TRADE_QUEUE[msg.message_id] = {
        'pair': pair, 'action': action, 'size': size,
        'entry_price': entry_price, 'sl': sl, 'tp': tp, 'leverage': leverage
    }

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    trade = TRADE_QUEUE.get(call.message.message_id)
    if not trade:
        bot.answer_callback_query(call.id, "Trade info not found.")
        return

    if call.data == "YES":
        bot.answer_callback_query(call.id, "Executing trade...")
        execute_trade(**trade)
    elif call.data == "NO":
        bot.answer_callback_query(call.id, "Trade cancelled.")

# ------------------------
# Main loop
# ------------------------
pair = "BTC/USDT"

while True:
    try:
        ohlcv = exchange.fetch_ohlcv(pair, timeframe='1m', limit=100)
        df = pd.DataFrame(ohlcv, columns=['timestamp','open','high','low','close','volume'])

        action, strategy_conf, triggered = aggregate_strategies(df)
        if not action:
            time.sleep(60)
            continue

        ml_pred = ml_predict(df, action, strategy_conf)
        if ml_pred < ADMIN_SETTINGS['ml_threshold']:
            time.sleep(60)
            continue

        balance = 1000  # replace with actual account balance fetch
        sl, tp, size, leverage = calculate_trade_params(df['close'].iloc[-1], action, balance, ADMIN_SETTINGS, pair)

        send_confirmation(ADMIN_ID, pair, action, strategy_conf, ml_pred, sl, tp, size, leverage, triggered, df['close'].iloc[-1])

        time.sleep(60)

    except Exception as e:
        print("Error:", e)
        time.sleep(60)
