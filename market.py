"""
pages/market.py — Market Data tab
"""
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import random
import core.state as state

SYMBOLS = state.SYMBOLS

def render():
    st.markdown("## 📡 Market Data")

    prices = st.session_state.prices

    # Ticker cards
    cols = st.columns(len(SYMBOLS))
    for i, sym in enumerate(SYMBOLS):
        p = prices[sym]
        base = state.BASE_PRICES[sym]
        chg = (p - base) / base * 100
        with cols[i]:
            st.metric(sym, f"${p:.2f}", f"{chg:+.2f}%")

    st.markdown("---")

    col_chart, col_book = st.columns([3, 1])

    with col_chart:
        sym_sel = st.selectbox("Symbol", SYMBOLS, key="chart_sym")
        interval = st.select_slider("Interval", ["1m", "5m", "15m", "1h"], value="15m")

        df = st.session_state.ohlcv.get(sym_sel)
        if df is not None and len(df) > 0:
            display = df.tail(60).copy()

            fig = go.Figure()

            # Candlestick
            fig.add_trace(go.Candlestick(
                x=display["date"], open=display["open"], high=display["high"],
                low=display["low"], close=display["close"],
                increasing_line_color="#28a745", decreasing_line_color="#dc3545",
                name="Price"
            ))

            # Moving averages
            fig.add_trace(go.Scatter(x=display["date"], y=display["ma20"], line=dict(color="#ffa500", width=1.5, dash="dot"), name="MA20"))
            fig.add_trace(go.Scatter(x=display["date"], y=display["ma50"], line=dict(color="#dc3545", width=1.5, dash="dot"), name="MA50"))

            fig.update_layout(
                height=320, margin=dict(l=0, r=0, t=10, b=0),
                xaxis_rangeslider_visible=False,
                plot_bgcolor="white", paper_bgcolor="white",
                legend=dict(orientation="h", yanchor="bottom", y=1.02),
                xaxis=dict(showgrid=False),
                yaxis=dict(tickprefix="$", showgrid=True, gridcolor="#f5f5f5"),
            )
            st.plotly_chart(fig, use_container_width=True)

            # RSI & MACD below
            c1, c2 = st.columns(2)
            with c1:
                rsi_val = display["rsi"].dropna()
                if len(rsi_val) > 0:
                    fig_rsi = go.Figure()
                    fig_rsi.add_trace(go.Scatter(y=rsi_val.values, line=dict(color="#6c5ce7", width=1.5), name="RSI"))
                    fig_rsi.add_hline(y=70, line_dash="dash", line_color="#dc3545", annotation_text="OB 70")
                    fig_rsi.add_hline(y=30, line_dash="dash", line_color="#28a745", annotation_text="OS 30")
                    fig_rsi.update_layout(height=140, margin=dict(l=0,r=0,t=20,b=0), plot_bgcolor="white", paper_bgcolor="white", showlegend=False, yaxis=dict(range=[0,100]))
                    st.markdown("**RSI(14)**")
                    st.plotly_chart(fig_rsi, use_container_width=True)
            with c2:
                macd = display["macd"].dropna()
                sig = display["signal_line"].dropna()
                if len(macd) > 0:
                    fig_macd = go.Figure()
                    fig_macd.add_trace(go.Scatter(y=macd.values, line=dict(color="#0984e3", width=1.5), name="MACD"))
                    fig_macd.add_trace(go.Scatter(y=sig.values, line=dict(color="#e17055", width=1.5, dash="dot"), name="Signal"))
                    fig_macd.update_layout(height=140, margin=dict(l=0,r=0,t=20,b=0), plot_bgcolor="white", paper_bgcolor="white", showlegend=False)
                    st.markdown("**MACD(12,26,9)**")
                    st.plotly_chart(fig_macd, use_container_width=True)

    with col_book:
        st.markdown("### 📖 Order Book")
        st.caption(f"{sym_sel}")
        mid = prices[sym_sel]
        book_data = []
        for i in range(5, 0, -1):
            book_data.append({"Type": "ASK", "Price": f"${mid + i*0.05:.2f}", "Size": random.randint(100, 2000)})
        for i in range(1, 6):
            book_data.append({"Type": "BID", "Price": f"${mid - i*0.05:.2f}", "Size": random.randint(100, 2000)})
        df_book = pd.DataFrame(book_data)
        st.dataframe(
            df_book.style.apply(lambda r: ["color:red" if r["Type"]=="ASK" else "color:green"]*len(r), axis=1),
            use_container_width=True, hide_index=True, height=280
        )

        st.markdown("### 💬 Sentiment")
        items = [
            ("Social Media", 72, "Bullish"),
            ("News Flow", 61, "Bullish"),
            ("Options Flow", 55, "Neutral"),
            ("Short Interest", 38, "Bearish"),
        ]
        for name, score, label in items:
            emoji = "🟢" if label == "Bullish" else "🟡" if label == "Neutral" else "🔴"
            st.markdown(f"{emoji} **{name}**: {label}")
            st.progress(score / 100)

    st.markdown("---")
    st.markdown("### 🔍 Stock Screener — ML-Ranked Opportunities")

    screener_rows = []
    for sym in SYMBOLS:
        df = st.session_state.ohlcv.get(sym)
        rsi = round(df["rsi"].iloc[-1], 1) if df is not None and not df["rsi"].isna().iloc[-1] else 50.0
        macd_val = df["macd"].iloc[-1] if df is not None else 0
        ma20 = df["ma20"].iloc[-1] if df is not None else 0
        ma50 = df["ma50"].iloc[-1] if df is not None else 1
        ml_score = random.randint(55, 97)
        chg = (prices[sym] - state.BASE_PRICES[sym]) / state.BASE_PRICES[sym] * 100
        screener_rows.append({
            "Symbol": sym,
            "Price": f"${prices[sym]:.2f}",
            "Change": f"{chg:+.2f}%",
            "Volume": f"{random.uniform(1, 50):.1f}M",
            "RSI": rsi,
            "MACD": "Bullish" if macd_val > 0 else "Bearish",
            "MA Signal": "BUY" if ma20 > ma50 else "HOLD",
            "ML Score": ml_score,
            "Action": "🚀 Strong Buy" if ml_score > 80 else "📈 Buy" if ml_score > 70 else "⏸ Hold",
        })

    screener_df = pd.DataFrame(screener_rows).sort_values("ML Score", ascending=False)
    st.dataframe(screener_df, use_container_width=True, hide_index=True)
