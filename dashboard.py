"""
pages/dashboard.py — Main dashboard tab
"""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import core.state as state

def render():
    st.markdown("## 📊 Live Dashboard")

    prices = st.session_state.prices
    positions = st.session_state.positions
    total_pnl = state.get_total_pnl()
    equity = 100000 + total_pnl

    # Top metrics
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Portfolio Value", f"${equity:,.0f}", f"${total_pnl:+,.0f}")
    c2.metric("Today's P&L", f"${total_pnl:+,.0f}", f"{total_pnl/1000:.2f}%")
    c3.metric("Win Rate", f"{st.session_state.win_rate:.1f}%", "+2.1%")
    c4.metric("Sharpe Ratio", f"{st.session_state.sharpe:.2f}", "+0.12")
    c5.metric("Open Positions", len(positions), f"{st.session_state.total_trades} trades today")

    st.markdown("---")

    col_left, col_right = st.columns([2, 1])

    with col_left:
        st.markdown("### 📈 Portfolio P&L (Live)")
        hist = st.session_state.pnl_history
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            y=hist,
            mode="lines",
            fill="tozeroy",
            line=dict(color="#28a745", width=2),
            fillcolor="rgba(40,167,69,0.1)",
            name="P&L",
        ))
        fig.update_layout(
            height=220, margin=dict(l=0, r=0, t=10, b=0),
            xaxis=dict(showticklabels=False, showgrid=False),
            yaxis=dict(tickprefix="$", showgrid=True, gridcolor="#f0f0f0"),
            plot_bgcolor="white", paper_bgcolor="white",
            showlegend=False,
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_right:
        st.markdown("### 🎯 Strategy Signals")
        for s in st.session_state.strategies:
            if s["enabled"]:
                pct = int(s["signal"] * 100)
                color = "🟢" if pct > 70 else "🟡" if pct > 50 else "🔴"
                st.markdown(f"**{s['name']}** {color} `{pct}%`")
                st.progress(pct / 100)

    st.markdown("---")
    col_pos, col_log = st.columns([3, 2])

    with col_pos:
        st.markdown("### 📋 Open Positions")
        if positions:
            rows = []
            for p in positions:
                cur = prices[p["sym"]]
                if p["side"] == "LONG":
                    pnl = (cur - p["entry"]) * p["qty"]
                else:
                    pnl = (p["entry"] - cur) * p["qty"]
                pct = pnl / (p["entry"] * p["qty"]) * 100
                rows.append({
                    "Symbol": p["sym"],
                    "Side": p["side"],
                    "Qty": p["qty"],
                    "Entry": f"${p['entry']:.2f}",
                    "Current": f"${cur:.2f}",
                    "P&L": f"${pnl:+.0f}",
                    "P&L %": f"{pct:+.2f}%",
                    "Stop": f"${p['sl']:.2f}",
                    "Target": f"${p['tp']:.2f}",
                })
            df = pd.DataFrame(rows)
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No open positions")

    with col_log:
        st.markdown("### 📜 Trade Log")
        log = st.session_state.trade_log[:20]
        for entry in log:
            icon = "🟢" if entry["type"] == "buy" else "🔴" if entry["type"] == "sell" else "⚪"
            st.markdown(f"<div class='trade-entry'>{icon} <b>{entry['time']}</b> — {entry['msg']}</div>", unsafe_allow_html=True)

    # Auto-refresh button
    st.markdown("---")
    col_r1, col_r2, col_r3 = st.columns([1, 1, 4])
    with col_r1:
        if st.button("🔄 Refresh", use_container_width=True):
            st.rerun()
    with col_r2:
        if st.button("⚡ Force Trade", use_container_width=True):
            state._auto_trade()
            st.rerun()
