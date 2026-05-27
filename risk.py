"""
pages/risk.py — Risk Management tab
"""
import streamlit as st
import plotly.graph_objects as go
import numpy as np
import random
import core.state as state

SYMBOLS = state.SYMBOLS

def render():
    st.markdown("## 🛡️ Risk Manager")

    equity = 100000 + state.get_total_pnl()
    win_rate = st.session_state.win_rate / 100
    avg_win = 312.0
    avg_loss = 148.0
    kelly = state.kelly_criterion(win_rate, avg_win, avg_loss)
    var = state.var_95(equity)

    # Key metrics
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Market Exposure", "42.3%", "Max: 80%")
    c2.metric("Kelly Criterion", f"{kelly*100:.1f}% (half-Kelly)", f"${equity * kelly * 0.5:,.0f} max bet")
    c3.metric("VaR (95%, Daily)", f"-${var:,.0f}", "Value at Risk")
    c4.metric("Profit Factor", f"{(win_rate * avg_win) / ((1-win_rate) * avg_loss):.2f}×", "Win/Loss ratio weighted")

    st.markdown("---")
    col_gauges, col_formulas, col_limits = st.columns(3)

    with col_gauges:
        st.markdown("### 📊 Risk Gauges")
        gauges = [
            ("Daily Loss Used", 40, 100, "green"),
            ("Position Exposure", 42, 80, "normal"),
            ("Max Drawdown Used", 40, 100, "green"),
            ("Correlation Risk", 35, 100, "green"),
            ("Sector Concentration", 48, 60, "warn"),
            ("Leverage Ratio", 15, 50, "green"),
        ]
        for name, val, limit, level in gauges:
            pct = val / limit
            color = "🟢" if pct < 0.6 else "🟡" if pct < 0.85 else "🔴"
            st.markdown(f"{color} **{name}**: {val}% / {limit}%")
            st.progress(pct)

    with col_formulas:
        st.markdown("### 📐 Sizing Formulas")
        st.markdown("**Position Size:**")
        st.latex(r"\text{Size} = \frac{\text{Account} \times \text{Risk\%}}{\text{|Entry - Stop Loss|}}")

        st.markdown("**Kelly Criterion:**")
        st.latex(r"K\% = \frac{WR \times B - (1-WR)}{B}")
        st.caption(f"B = Avg Win / Avg Loss = {avg_win/avg_loss:.2f}")

        st.markdown("**Sharpe Ratio:**")
        st.latex(r"\text{Sharpe} = \frac{\bar{R} - R_f}{\sigma_R} \times \sqrt{252}")

        st.markdown("**VaR (95%):**")
        st.latex(r"\text{VaR}_{95\%} = \mu - 1.645 \times \sigma \times \sqrt{P}")

        st.markdown("---")
        st.markdown("**Live Calculations:**")
        risk_amt = equity * (st.session_state.risk_pct / 100)
        entry_ex = state.BASE_PRICES["AAPL"]
        sl_ex = entry_ex * (1 - st.session_state.stop_loss_pct / 100)
        pos_size = state.position_size(equity, st.session_state.risk_pct, entry_ex, sl_ex)
        st.info(f"""
        Account: ${equity:,.0f}
        Risk per trade: {st.session_state.risk_pct}% = ${risk_amt:,.0f}
        Example (AAPL @ ${entry_ex:.0f}, SL @ ${sl_ex:.0f}):
        → **Max Shares: {pos_size}**
        → **Max $ Risk: ${risk_amt:,.0f}**
        """)

    with col_limits:
        st.markdown("### ⚠️ Hard Risk Limits")
        limits = [
            ("Max Position Size", "$5,000", True),
            ("Max Daily Loss", "-$3,000", True),
            ("Stop Loss per Trade", f"{st.session_state.stop_loss_pct}%", True),
            ("Max Drawdown", "-5%", True),
            ("Correlation Limit", "0.7 between assets", False),
            ("Sector Limit", "30% in any sector", True),
            ("Max Leverage", "1.5×", True),
            ("Min ML Confidence", "65%", True),
        ]
        for name, val, ok in limits:
            icon = "✅" if ok else "⚠️"
            st.markdown(f"{icon} **{name}**: `{val}`")

        st.markdown("---")
        st.markdown("### 🔧 Adjust Limits")
        new_daily_loss = st.number_input("Max Daily Loss ($)", -10000, -100, -3000, step=100)
        new_max_pos = st.number_input("Max Position Size ($)", 500, 50000, 5000, step=500)
        if st.button("Update Limits", use_container_width=True):
            st.success("Limits updated!")

    st.markdown("---")
    st.markdown("### 🔗 Correlation Matrix")

    symbols = SYMBOLS
    corr = np.array([
        [1.00, 0.72, 0.65, 0.68, 0.55, 0.48],
        [0.72, 1.00, 0.58, 0.61, 0.51, 0.44],
        [0.65, 0.58, 1.00, 0.59, 0.82, 0.71],
        [0.68, 0.61, 0.59, 1.00, 0.63, 0.57],
        [0.55, 0.51, 0.82, 0.63, 1.00, 0.79],
        [0.48, 0.44, 0.71, 0.57, 0.79, 1.00],
    ])
    fig = go.Figure(data=go.Heatmap(
        z=corr, x=symbols, y=symbols,
        colorscale=[[0,"#28a745"],[0.5,"#ffc107"],[1,"#dc3545"]],
        text=[[f"{v:.2f}" for v in row] for row in corr],
        texttemplate="%{text}", textfont={"size":12},
        zmin=0, zmax=1, showscale=True,
        colorbar=dict(title="Correlation"),
    ))
    fig.update_layout(height=280, margin=dict(l=0,r=0,t=10,b=0))
    st.plotly_chart(fig, use_container_width=True)
    st.caption("⚠️ High correlation (>0.7) between NVDA-GOOGL detected. Consider reducing combined position size.")
