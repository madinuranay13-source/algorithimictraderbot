# 📈 AlgoTrader Pro

A professional-grade algorithmic trading dashboard built with Python and Streamlit. Features live simulated market data, multiple trading strategies, risk management, backtesting, and portfolio optimization.

## 🚀 Live Demo
[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io)

## ✨ Features

### 5 Core Systems
| System | Description |
|--------|-------------|
| 📡 Market Data | Live ticking prices, order book, OHLCV charts, RSI/MACD/MA indicators, screener |
| 🧠 Strategy Engine | MA Crossover, RSI Mean Reversion, MACD Momentum, ML Ensemble, Pairs Trading |
| 🛡️ Risk Manager | Kelly Criterion, VaR, position sizing, correlation matrix, hard limits |
| ⏮️ Backtester | Equity curve vs S&P 500, Sharpe, max drawdown, monthly returns heatmap |
| 💼 Portfolio | Markowitz MPT, efficient frontier, rebalancing suggestions |

### Key Formulas Implemented
```
Position Size  = (Account × Risk%) / |Entry - Stop Loss|
Kelly %        = (WR × B - (1-WR)) / B   where B = AvgWin/AvgLoss
Sharpe Ratio   = (Avg_Return - Rf) / σ × √252
VaR (95%)      = μ - 1.645 × σ × √Portfolio
```

## 🛠️ Installation & Setup

### Option 1: Local (Fastest)
```bash
git clone https://github.com/YOUR_USERNAME/algotrader-pro
cd algotrader-pro
pip install -r requirements.txt
streamlit run app.py
```
Open http://localhost:8501

### Option 2: Streamlit Community Cloud (Free, Public URL)
1. Push to GitHub (see below)
2. Go to https://share.streamlit.io
3. Click "New app" → pick your repo → `app.py` → Deploy

### Option 3: Docker
```bash
docker build -t algotrader .
docker run -p 8501:8501 algotrader
# Open http://localhost:8501
```

## 📁 Project Structure
```
algotrader-pro/
├── app.py              # Main entry point + sidebar
├── requirements.txt    # Dependencies
├── core/
│   └── state.py        # State, simulation engine, formulas
├── pages/
│   ├── dashboard.py    # Live P&L, positions, trade log
│   ├── market.py       # Price charts, order book, screener
│   ├── strategy.py     # Strategy config, signal heatmap
│   ├── risk.py         # Risk gauges, VaR, correlation
│   ├── backtest.py     # Historical simulation
│   └── portfolio.py    # MPT, efficient frontier
└── README.md
```

## 🐙 GitHub Setup (Step by Step)
```bash
# 1. Initialize git
cd algotrader-pro
git init
git add .
git commit -m "Initial commit: AlgoTrader Pro"

# 2. Create repo on GitHub at https://github.com/new
# 3. Push
git remote add origin https://github.com/YOUR_USERNAME/algotrader-pro.git
git branch -M main
git push -u origin main
```

## ⚠️ Disclaimer
This is a **paper trading simulator** for educational purposes only.
It uses **simulated data** — not real market prices.
**Do NOT use this with real money without extensive testing.**
Always consult a licensed financial advisor.

## 📜 License
MIT License — free to use and modify.
