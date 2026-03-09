import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# Page setup
st.set_page_config(page_title="Trading Dashboard", layout="wide")
st.title("📊 Multi-Chart Trading Dashboard")

# Sidebar controls
st.sidebar.header("Chart Settings")

# Symbol selection
symbols = {
    "BTC/USD": "BTC-USD",
    "ETH/USD": "ETH-USD",
    "Gold": "GC=F",
    "US100 (NASDAQ)": "^NDX",
    "US30 (Dow Jones)": "^DJI",
    "GER40 (DAX)": "^GDAXI",
    "UK100 (FTSE)": "^FTSE"
}
symbol_label = st.sidebar.selectbox("Select Symbol", list(symbols.keys()))
symbol = symbols[symbol_label]

# Timeframe selection
interval = st.sidebar.selectbox("Timeframe", ["1m", "5m", "15m", "1h", "1d"])

# Determine max period allowed
if interval == "1m":
    period = "7d"
elif interval == "5m":
    period = "60d"
elif interval == "15m":
    period = "60d"
else:
    period = "1y"

# Load data
st.write(f"Loading data for {symbol_label} ({interval})...")
ticker = yf.Ticker(symbol)
hist = ticker.history(period=period, interval=interval)

# If no data fallback to daily
if hist.empty and interval != "1d":
    st.warning("⚠️ No data in selected interval. Falling back to daily candles.")
    interval = "1d"
    period = "1y"
    hist = ticker.history(period=period, interval=interval)

if hist.empty:
    st.error("❌ No data available for this symbol/timeframe.")
else:
    # Ensure datetime index
    hist.index = pd.to_datetime(hist.index)

    # Date range picker (defaults to last 7 days)
    date_range = st.sidebar.date_input(
        "Select Date Range",
        value=(
            pd.Timestamp.today() - pd.Timedelta(days=7),
            pd.Timestamp.today()
        )
    )

    # Filter by date
    start_date = pd.to_datetime(date_range[0]).tz_localize(hist.index.tz)
    end_date = pd.to_datetime(date_range[1]).tz_localize(hist.index.tz)

    hist = hist[
        (hist.index >= start_date) &
        (hist.index <= end_date + pd.Timedelta(days=1))
    ]

    if hist.empty:
        st.warning("⚠️ No data available for this date range.")
    else:
        # Chart type
        chart_type = st.sidebar.radio(
            "Chart Type",
            ["🕯️ Basic Candlestick Chart", "🕯️ Advanced Candlestick Chart with Patterns"]
        )

        # Pattern detection
        def detect_patterns(row):
            o, h, l, c = row["Open"], row["High"], row["Low"], row["Close"]
            body = abs(c - o)
            candle_range = h - l
            upper_shadow = h - max(o, c)
            lower_shadow = min(o, c) - l

            if candle_range == 0:
                return ""

            body_ratio = body / candle_range
            upper_ratio = upper_shadow / candle_range
            lower_ratio = lower_shadow / candle_range

            if body_ratio < 0.1:
                return "Doji"
            if body_ratio > 0.2 and lower_ratio > 0.5 and upper_ratio < 0.2:
                return "Hammer"
            if body_ratio > 0.2 and upper_ratio > 0.5 and lower_ratio < 0.2:
                return "Inverted Hammer"
            if body_ratio > 0.2 and upper_ratio > 0.5 and lower_ratio < 0.2 and o > c:
                return "Shooting Star"
            if c > o and body_ratio > 0.5:
                return "Bullish Engulfing"
            if o > c and body_ratio > 0.5:
                return "Bearish Engulfing"
            return ""

        if chart_type == "🕯️ Advanced Candlestick Chart with Patterns":
            hist["Pattern"] = hist.apply(detect_patterns, axis=1)
        else:
            hist["Pattern"] = ""

        # Build figure
        st.subheader(chart_type)
        fig = go.Figure()

        fig.add_trace(go.Candlestick(
            x=hist.index,
            open=hist["Open"],
            high=hist["High"],
            low=hist["Low"],
            close=hist["Close"],
            name="Candlesticks",
            increasing_line_color="lime",
            decreasing_line_color="red",
            increasing_fillcolor="rgba(0,255,0,0.4)",
            decreasing_fillcolor="rgba(255,0,0,0.4)"
        ))

        if chart_type == "🕯️ Advanced Candlestick Chart with Patterns":
            for idx, row in hist.iterrows():
                if row["Pattern"]:
                    fig.add_trace(go.Scatter(
                        x=[idx],
                        y=[row["High"]],
                        mode="markers+text",
                        marker=dict(color="yellow", size=10, symbol="star"),
                        text=row["Pattern"],
                        textposition="top center",
                        name=row["Pattern"]
                    ))

        fig.update_layout(
            template="plotly_dark",
            height=650,
            margin=dict(l=20, r=20, t=40, b=20),
            xaxis_rangeslider_visible=True,
            dragmode="pan",
            xaxis_title="Time",
            yaxis_title="Price",
            hovermode="x unified"
        )
        st.plotly_chart(fig, use_container_width=True)

        st.caption(
            "✅ Use your mouse wheel to zoom, drag to pan, and pick date range in the sidebar."
        )
