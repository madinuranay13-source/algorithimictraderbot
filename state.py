"""
core/state.py — Shared state, simulation engine, and formulas
"""
import streamlit as st
import numpy as np
import pandas as pd
import random
from datetime import datetime, timedelta

SYMBOLS = ["AAPL", "TSLA", "NVDA", "MSFT", "GOOGL", "AMZN"]
BASE_PRICES = {"AAPL": 189.0, "TSLA": 248.0, "NVDA": 875.0, "MSFT": 412.0, "GOOGL": 175.0, "AMZN": 185.0}
SECTORS = {"AAPL": "Tech", "TSLA": "Auto/EV", "NVDA": "Semiconductors", "MSFT": "Tech", "GOOGL": "Adtech", "AMZN": "E-Commerce"}

def now():
    return datetime.now().strftime("%H:%M:%S")

def init():
    if "initialized" in st.session_state:
        return

    st.session_state.initialized = True
    st.session_state.bot_running = True
    st.session_state.tick_count = 0
    st.session_state.risk_pct = 1.0
    st.session_state.max_positions = 5
    st.session_state.stop_loss_pct = 2.0
    st.session_state.win_rate = 67.3
    st.session_state.sharpe = 2.41
    st.session_state.total_trades = 38
    st.session_state.wins = 25
    st.session_state.losses = 13
    st.session_state.equity = 100000.0

    # Live prices
    st.session_state.prices = {s: BASE_PRICES[s] + random.uniform(-2, 2) for s in SYMBOLS}

    # Positions
    st.session_state.positions = [
        {"sym": "AAPL", "side": "LONG",  "qty": 50,  "entry": 185.20, "sl": 182.00, "tp": 195.00},
        {"sym": "NVDA", "side": "LONG",  "qty": 10,  "entry": 860.00, "sl": 840.00, "tp": 920.00},
        {"sym": "MSFT", "side": "LONG",  "qty": 25,  "entry": 408.50, "sl": 400.00, "tp": 425.00},
        {"sym": "TSLA", "side": "SHORT", "qty": 15,  "entry": 255.00, "sl": 263.00, "tp": 238.00},
        {"sym": "GOOGL","side": "LONG",  "qty": 30,  "entry": 172.00, "sl": 168.00, "tp": 182.00},
    ]

    # P&L history (last 90 ticks)
    base = 0.0
    hist = []
    for _ in range(90):
        base += random.gauss(25, 120)
        hist.append(base)
    st.session_state.pnl_history = hist

    # Trade log
    st.session_state.trade_log = [
        {"time": now(), "msg": "BOT INITIALIZED — All systems operational", "type": "info"},
        {"time": now(), "msg": "Strategy engine loaded: 4 active strategies", "type": "info"},
        {"time": now(), "msg": "Risk limits configured — Max drawdown: 5%", "type": "info"},
        {"time": now(), "msg": "Market data feed connected — 6 symbols", "type": "info"},
    ]

    # Strategies
    st.session_state.strategies = [
        {"name": "MA Crossover",   "enabled": True,  "signal": 0.72, "trades": 14, "win_rate": 71, "ma_short": 20, "ma_long": 50},
        {"name": "RSI Mean Rev",   "enabled": True,  "signal": 0.55, "trades": 8,  "win_rate": 62, "rsi_period": 14, "rsi_ob": 70, "rsi_os": 30},
        {"name": "MACD Momentum",  "enabled": True,  "signal": 0.81, "trades": 11, "win_rate": 73, "macd_fast": 12, "macd_slow": 26},
        {"name": "ML Ensemble",    "enabled": True,  "signal": 0.88, "trades": 5,  "win_rate": 80, "confidence": 75},
        {"name": "Pairs Trading",  "enabled": False, "signal": 0.30, "trades": 0,  "win_rate": 0},
    ]

    # Historical OHLCV per symbol
    st.session_state.ohlcv = {s: generate_ohlcv(BASE_PRICES[s], 100) for s in SYMBOLS}

    st.session_state.backtest_run = False

def generate_ohlcv(base_price, n=100):
    dates = pd.date_range(end=datetime.now(), periods=n, freq="15min")
    prices = [base_price]
    for _ in range(n - 1):
        prices.append(max(prices[-1] * (1 + random.gauss(0.0002, 0.005)), base_price * 0.7))
    opens, highs, lows, closes, vols = [], [], [], [], []
    for p in prices:
        o = p * (1 + random.uniform(-0.002, 0.002))
        c = p * (1 + random.uniform(-0.003, 0.003))
        h = max(o, c) * (1 + random.uniform(0, 0.003))
        l = min(o, c) * (1 - random.uniform(0, 0.003))
        opens.append(round(o, 2)); highs.append(round(h, 2)); lows.append(round(l, 2))
        closes.append(round(c, 2)); vols.append(int(random.uniform(500000, 5000000)))
    df = pd.DataFrame({"date": dates, "open": opens, "high": highs, "low": lows, "close": closes, "volume": vols})
    # Add indicators
    df["ma20"] = df["close"].rolling(20).mean()
    df["ma50"] = df["close"].rolling(50).mean()
    df["rsi"] = compute_rsi(df["close"], 14)
    df["macd"], df["signal_line"] = compute_macd(df["close"])
    return df

def compute_rsi(series, period=14):
    delta = series.diff()
    gain = delta.clip(lower=0).rolling(period).mean()
    loss = (-delta.clip(upper=0)).rolling(period).mean()
    rs = gain / loss.replace(0, 1e-9)
    return 100 - (100 / (1 + rs))

def compute_macd(series, fast=12, slow=26, signal=9):
    ema_fast = series.ewm(span=fast).mean()
    ema_slow = series.ewm(span=slow).mean()
    macd = ema_fast - ema_slow
    signal_line = macd.ewm(span=signal).mean()
    return macd, signal_line

def get_total_pnl():
    total = 4218.0  # realized gains
    for p in st.session_state.positions:
        cur = st.session_state.prices[p["sym"]]
        if p["side"] == "LONG":
            total += (cur - p["entry"]) * p["qty"]
        else:
            total += (p["entry"] - cur) * p["qty"]
    return total

def kelly_criterion(win_rate, avg_win, avg_loss):
    """Kelly % = (W * B - L) / B  where B = avg_win/avg_loss"""
    if avg_loss == 0:
        return 0
    b = avg_win / avg_loss
    return max(0, (win_rate * b - (1 - win_rate)) / b)

def position_size(account_value, risk_pct, entry_price, stop_loss_price):
    """Position Size = (Account × Risk%) / Stop Distance"""
    risk_amount = account_value * (risk_pct / 100)
    stop_distance = abs(entry_price - stop_loss_price)
    if stop_distance == 0:
        return 0
    return int(risk_amount / stop_distance)

def sharpe_ratio(returns, rf=0.05):
    """Sharpe = (Avg_return - Rf) / Std × √252"""
    if len(returns) < 2:
        return 0
    excess = np.array(returns) - rf / 252
    if np.std(excess) == 0:
        return 0
    return float(np.mean(excess) / np.std(excess) * np.sqrt(252))

def max_drawdown(equity_curve):
    peak = equity_curve[0]
    max_dd = 0
    for v in equity_curve:
        if v > peak:
            peak = v
        dd = (peak - v) / peak
        if dd > max_dd:
            max_dd = dd
    return max_dd

def var_95(portfolio_value, daily_vol=0.015):
    """VaR(95%) = μ - 1.645 × σ × Portfolio"""
    return portfolio_value * 1.645 * daily_vol

def tick():
    """Simulate one market tick"""
    st.session_state.tick_count += 1
    prices = st.session_state.prices

    # Update prices
    for s in SYMBOLS:
        chg = random.gauss(0.0003, 0.003)
        prices[s] = max(prices[s] * (1 + chg), BASE_PRICES[s] * 0.75)

    # Update P&L history
    pnl = get_total_pnl()
    st.session_state.pnl_history.append(pnl)
    if len(st.session_state.pnl_history) > 120:
        st.session_state.pnl_history.pop(0)

    # Auto-trade logic
    if random.random() < 0.2:
        _auto_trade()

    # Update strategy signals
    for s in st.session_state.strategies:
        if s["enabled"]:
            s["signal"] = max(0.3, min(0.97, s["signal"] + random.gauss(0, 0.02)))

    # Update stats
    st.session_state.win_rate = max(55, min(85, st.session_state.win_rate + random.gauss(0, 0.1)))
    st.session_state.sharpe = max(1.5, min(4.0, st.session_state.sharpe + random.gauss(0, 0.02)))

    # Check stops/targets
    _check_risk_triggers()

def _auto_trade():
    """Bot auto-generates trades based on signals"""
    sym = random.choice(SYMBOLS)
    prices = st.session_state.prices
    price = prices[sym]

    # Entry conditions check
    df = st.session_state.ohlcv.get(sym)
    if df is None or len(df) < 51:
        return

    rsi = df["rsi"].iloc[-1]
    ma20 = df["ma20"].iloc[-1]
    ma50 = df["ma50"].iloc[-1]
    macd = df["macd"].iloc[-1]
    ml_conf = random.uniform(60, 95)

    # Buy signal: MA20 > MA50 AND RSI < 70 AND MACD > 0 AND ML > 65
    if (ma20 > ma50) and (rsi < 70) and (macd > 0) and (ml_conf > 65) and (random.random() < 0.4):
        qty = position_size(st.session_state.equity, st.session_state.risk_pct, price, price * 0.98)
        qty = max(1, min(qty, 50))
        st.session_state.trade_log.insert(0, {
            "time": now(),
            "msg": f"BUY {qty}×{sym} @ ${price:.2f} | RSI:{rsi:.0f} MA✓ MACD✓ ML:{ml_conf:.0f}%",
            "type": "buy"
        })
        st.session_state.total_trades += 1
        outcome = random.random()
        if outcome < st.session_state.win_rate / 100:
            st.session_state.wins += 1
        else:
            st.session_state.losses += 1

    # Sell signal
    elif (ma20 < ma50) and (rsi > 60) and (random.random() < 0.3):
        st.session_state.trade_log.insert(0, {
            "time": now(),
            "msg": f"SELL signal {sym} @ ${price:.2f} | MA bearish cross | RSI:{rsi:.0f}",
            "type": "sell"
        })

    if len(st.session_state.trade_log) > 60:
        st.session_state.trade_log = st.session_state.trade_log[:60]

def _check_risk_triggers():
    """Check stop loss and take profit for all positions"""
    prices = st.session_state.prices
    for pos in list(st.session_state.positions):
        cur = prices[pos["sym"]]
        if pos["side"] == "LONG":
            if cur <= pos["sl"]:
                pnl = (cur - pos["entry"]) * pos["qty"]
                st.session_state.trade_log.insert(0, {
                    "time": now(),
                    "msg": f"STOP LOSS hit — {pos['sym']} @ ${cur:.2f} | Loss: ${pnl:+.0f}",
                    "type": "sell"
                })
            elif cur >= pos["tp"]:
                pnl = (cur - pos["entry"]) * pos["qty"]
                st.session_state.trade_log.insert(0, {
                    "time": now(),
                    "msg": f"TAKE PROFIT hit — {pos['sym']} @ ${cur:.2f} | Gain: ${pnl:+.0f}",
                    "type": "buy"
                })
