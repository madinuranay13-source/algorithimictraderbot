"""
AlgoTrader Pro — Streamlit Algorithmic Trading Dashboard
"""
import streamlit as st

st.set_page_config(
    page_title="AlgoTrader Pro",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS
st.markdown("""
<style>
    .main { padding-top: 1rem; }
    .stMetric { background: #f8f9fa; border-radius: 8px; padding: 12px; border: 1px solid #e9ecef; }
    .stMetric label { font-size: 12px !important; color: #6c757d !important; }
    div[data-testid="metric-container"] { background: #f8f9fa; border-radius: 8px; padding: 12px; border: 1px solid #e9ecef; }
    .signal-box { padding: 8px 12px; border-radius: 6px; margin: 4px 0; font-size: 14px; }
    .signal-buy  { background: #d4edda; color: #155724; border-left: 4px solid #28a745; }
    .signal-sell { background: #f8d7da; color: #721c24; border-left: 4px solid #dc3545; }
    .signal-hold { background: #fff3cd; color: #856404; border-left: 4px solid #ffc107; }
    .trade-entry { font-size: 12px; padding: 4px 0; border-bottom: 1px solid #eee; }
    h1 { font-size: 24px !important; }
    h2 { font-size: 18px !important; }
    h3 { font-size: 15px !important; }
</style>
""", unsafe_allow_html=True)

import state

state.init()

# Sidebar
with st.sidebar:
    st.markdown("## ⚙️ AlgoTrader Pro")
    st.markdown("---")

    bot_running = st.session_state.get("bot_running", True)
    if bot_running:
        if st.button("⏹ Stop Bot", use_container_width=True, type="secondary"):
            st.session_state.bot_running = False
            st.session_state.trade_log.insert(0, {"time": state.now(), "msg": "BOT STOPPED — holding all positions", "type": "warn"})
            st.rerun()
    else:
        if st.button("▶ Start Bot", use_container_width=True, type="primary"):
            st.session_state.bot_running = True
            st.session_state.trade_log.insert(0, {"time": state.now(), "msg": "BOT STARTED — resuming strategies", "type": "info"})
            st.rerun()

    status = "🟢 LIVE — Paper Trading" if bot_running else "🔴 STOPPED"
    st.markdown(f"**Status:** {status}")
    st.markdown("---")

    st.markdown("### 📊 Quick Stats")
    total_pnl = state.get_total_pnl()
    st.metric("Total P&L", f"${total_pnl:+,.0f}", f"{total_pnl/100000*100:+.2f}%")
    st.metric("Win Rate", f"{st.session_state.win_rate:.1f}%")
    st.metric("Sharpe Ratio", f"{st.session_state.sharpe:.2f}")
    st.metric("Open Positions", len(st.session_state.positions))

    st.markdown("---")
    st.markdown("### 🔧 Global Settings")
    st.session_state.risk_pct = st.slider("Risk per Trade %", 0.5, 5.0, st.session_state.get("risk_pct", 1.0), 0.1)
    st.session_state.max_positions = st.slider("Max Positions", 1, 10, st.session_state.get("max_positions", 5))
    st.session_state.stop_loss_pct = st.slider("Stop Loss %", 0.5, 5.0, st.session_state.get("stop_loss_pct", 2.0), 0.1)

    st.markdown("---")
    st.caption("AlgoTrader Pro v1.0 | Paper Trading Mode")
    st.caption("⚠️ For educational use only. Not financial advice.")

# Simulate tick if bot running
if st.session_state.bot_running:
    state.tick()

# Navigation tabs
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📊 Dashboard", "📡 Market Data", "🧠 Strategy Engine",
    "🛡️ Risk Manager", "⏮️ Backtest", "💼 Portfolio"
])

with tab1:
    from pages import dashboard
    dashboard.render()

with tab2:
    from pages import market
    market.render()

with tab3:
    from pages import strategy
    strategy.render()

with tab4:
    from pages import risk
    risk.render()

with tab5:
    from pages import backtest
    backtest.render()

with tab6:
    from pages import portfolio
    portfolio.render()
