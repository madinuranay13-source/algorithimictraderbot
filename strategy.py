"""
pages/strategy.py — Strategy Engine tab
"""
import streamlit as st
import plotly.graph_objects as go
import numpy as np
import random
import core.state as state

SYMBOLS = state.SYMBOLS

def render():
    st.markdown("## 🧠 Strategy Engine")

    strategies = st.session_state.strategies

    col_strats, col_params = st.columns(2)

    with col_strats:
        st.markdown("### Active Strategies")
        for i, s in enumerate(strategies):
            with st.expander(f"{'✅' if s['enabled'] else '❌'} {s['name']} — WR: {s['win_rate']}% | Trades: {s['trades']}", expanded=s["enabled"]):
                enabled = st.toggle("Enable", value=s["enabled"], key=f"toggle_{i}")
                strategies[i]["enabled"] = enabled

                pct = int(s["signal"] * 100)
                color = "🟢" if pct > 70 else "🟡" if pct > 50 else "🔴"
                st.markdown(f"**Signal Strength:** {color} `{pct}%`")
                st.progress(pct / 100)
                st.caption(f"Trades: {s['trades']} | Win Rate: {s['win_rate']}%")

        st.markdown("---")
        st.markdown("### 🔬 Entry Conditions (AND Logic)")
        prices = st.session_state.prices
        sym = "AAPL"
        df = st.session_state.ohlcv.get(sym)
        if df is not None and len(df) > 51:
            ma20 = df["ma20"].iloc[-1]
            ma50 = df["ma50"].iloc[-1]
            rsi = df["rsi"].iloc[-1]
            macd = df["macd"].iloc[-1]
            vol = df["volume"].iloc[-1]
            avg_vol = df["volume"].rolling(20).mean().iloc[-1]
            ml_conf = random.uniform(65, 95)

            conditions = [
                (f"MA₂₀ ({ma20:.2f}) > MA₅₀ ({ma50:.2f})", ma20 > ma50),
                (f"RSI ({rsi:.1f}) < 70 (Not Overbought)", rsi < 70),
                (f"Volume ({vol/1e6:.1f}M) > 1.5× Avg", vol > avg_vol * 1.5),
                (f"MACD Histogram > 0 ({macd:.3f})", macd > 0),
                (f"ML Confidence > 65% ({ml_conf:.0f}%)", ml_conf > 65),
            ]
            all_met = all(c[1] for c in conditions)
            for cond_text, met in conditions:
                icon = "✅" if met else "⚠️"
                st.markdown(f"{icon} {cond_text}")

            if all_met:
                st.success("🚀 ALL CONDITIONS MET — Bot would enter trade")
            else:
                failed = sum(1 for _, m in conditions if not m)
                st.warning(f"⏸ {failed} condition(s) not met — No trade")

    with col_params:
        st.markdown("### ⚙️ Strategy Parameters")

        tab_ma, tab_rsi, tab_macd, tab_ml = st.tabs(["MA Cross", "RSI", "MACD", "ML"])

        with tab_ma:
            st.markdown("**Moving Average Crossover**")
            ma_short = st.slider("Short Window", 5, 50, 20, key="ma_short")
            ma_long = st.slider("Long Window", 20, 200, 50, key="ma_long")
            ma_vol_filter = st.checkbox("Volume Filter (1.5× avg)", value=True)
            st.info(f"Signal: Buy when MA{ma_short} crosses above MA{ma_long}")
            st.latex(r"\text{Signal} = \begin{cases} BUY & MA_{" + str(ma_short) + r"} > MA_{" + str(ma_long) + r"} \\ SELL & MA_{" + str(ma_short) + r"} < MA_{" + str(ma_long) + r"} \end{cases}")

        with tab_rsi:
            st.markdown("**RSI Mean Reversion**")
            rsi_period = st.slider("RSI Period", 5, 30, 14, key="rsi_p")
            rsi_ob = st.slider("Overbought Level", 60, 90, 70, key="rsi_ob")
            rsi_os = st.slider("Oversold Level", 10, 40, 30, key="rsi_os")
            st.info(f"Buy when RSI < {rsi_os}, Sell when RSI > {rsi_ob}")
            st.latex(r"RSI = 100 - \frac{100}{1 + \frac{\text{Avg Gain}}{\text{Avg Loss}}}")

        with tab_macd:
            st.markdown("**MACD Momentum**")
            macd_fast = st.slider("Fast EMA", 5, 30, 12, key="mf")
            macd_slow = st.slider("Slow EMA", 15, 60, 26, key="ms")
            macd_sig = st.slider("Signal Line", 5, 20, 9, key="msig")
            st.info(f"MACD({macd_fast},{macd_slow},{macd_sig})")
            st.latex(r"MACD = EMA_{" + str(macd_fast) + r"} - EMA_{" + str(macd_slow) + r"}")

        with tab_ml:
            st.markdown("**ML Ensemble Model**")
            ml_conf_thresh = st.slider("Min Confidence %", 50, 90, 70, key="mlc")
            ml_lookback = st.slider("Lookback Window (bars)", 10, 100, 30, key="mll")
            features = st.multiselect("Features", ["RSI", "MACD", "MA Ratio", "Volume Z-Score", "ATR", "Momentum", "BB Width"], default=["RSI", "MACD", "MA Ratio", "Volume Z-Score"])
            st.caption(f"Using {len(features)} features | Threshold: {ml_conf_thresh}%")
            st.info("Gradient Boosting Ensemble: XGBoost + Random Forest + LSTM blend")

        st.markdown("---")
        st.markdown("### 🔥 ML Signal Heatmap")
        indicators = ["RSI", "MACD", "MA Cross", "Volume", "ML Score"]
        z_data = [[random.randint(20, 97) for _ in indicators] for _ in SYMBOLS]
        fig = go.Figure(data=go.Heatmap(
            z=z_data, x=indicators, y=SYMBOLS,
            colorscale=[[0,"#dc3545"],[0.5,"#ffc107"],[1,"#28a745"]],
            text=[[f"{v}%" for v in row] for row in z_data],
            texttemplate="%{text}", textfont={"size":11},
            zmin=0, zmax=100, showscale=True,
        ))
        fig.update_layout(height=220, margin=dict(l=0,r=0,t=10,b=0))
        st.plotly_chart(fig, use_container_width=True)

    if st.button("🔄 Refresh Signals"):
        st.rerun()
