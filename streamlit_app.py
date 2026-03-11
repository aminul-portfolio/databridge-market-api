import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go


# -----------------------------
# Page setup
# -----------------------------
st.set_page_config(
    page_title="DataBridge Market Dashboard",
    page_icon="📈",
    layout="wide",
)

st.markdown(
    """
    <style>
        .main {
            padding-top: 1rem;
        }
        .db-hero {
            padding: 1.2rem 1.4rem;
            border: 1px solid rgba(15, 23, 42, 0.08);
            border-radius: 20px;
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
            color: white;
            margin-bottom: 1rem;
            box-shadow: 0 10px 24px rgba(15, 23, 42, 0.18);
        }
        .db-kicker {
            margin: 0 0 0.35rem 0;
            font-size: 0.78rem;
            font-weight: 700;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            color: #a5b4fc;
        }
        .db-title {
            margin: 0;
            font-size: 2rem;
            font-weight: 800;
            color: #ffffff;
        }
        .db-subtitle {
            margin: 0.45rem 0 0 0;
            color: #cbd5e1;
            font-size: 0.98rem;
            line-height: 1.5;
        }
        .db-badge-row {
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
            margin-top: 0.9rem;
        }
        .db-badge {
            display: inline-flex;
            align-items: center;
            min-height: 34px;
            padding: 0.45rem 0.8rem;
            border-radius: 999px;
            font-size: 0.85rem;
            font-weight: 700;
            background: rgba(255, 255, 255, 0.08);
            border: 1px solid rgba(255, 255, 255, 0.12);
            color: #e2e8f0;
        }
        .db-section-card {
            padding: 1rem 1.1rem;
            border: 1px solid rgba(15, 23, 42, 0.08);
            border-radius: 18px;
            background: #ffffff;
            box-shadow: 0 10px 24px rgba(15, 23, 42, 0.06);
            margin-bottom: 1rem;
        }
        .db-section-title {
            margin: 0 0 0.35rem 0;
            font-size: 1.05rem;
            font-weight: 800;
            color: #0f172a;
        }
        .db-section-copy {
            margin: 0;
            font-size: 0.92rem;
            color: #64748b;
        }
        .db-footnote {
            font-size: 0.86rem;
            color: #64748b;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="db-hero">
        <p class="db-kicker">DataBridge Market API</p>
        <h1 class="db-title">Market Analytics Dashboard</h1>
        <p class="db-subtitle">
            A branded Streamlit analytics surface for reviewing market price action,
            timeframe-level trends, candlestick structures, and portfolio-style chart interactions.
            This dashboard complements the broader DataBridge platform by providing a fast visual layer
            for analyst review and exploratory inspection.
        </p>
        <div class="db-badge-row">
            <span class="db-badge">ETL-Oriented Project</span>
            <span class="db-badge">Analytics Engineer Portfolio</span>
            <span class="db-badge">FinTech / BI Ready</span>
            <span class="db-badge">Interactive Charting</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# -----------------------------
# Sidebar controls
# -----------------------------
st.sidebar.header("DataBridge Controls")

symbols = {
    "BTC/USD": "BTC-USD",
    "ETH/USD": "ETH-USD",
    "Gold": "GC=F",
    "US100 (NASDAQ)": "^NDX",
    "US30 (Dow Jones)": "^DJI",
    "GER40 (DAX)": "^GDAXI",
    "UK100 (FTSE)": "^FTSE",
}

symbol_label = st.sidebar.selectbox("Instrument", list(symbols.keys()))
symbol = symbols[symbol_label]

ui_interval = st.sidebar.selectbox("Timeframe", ["1m", "5m", "15m", "1h", "1d"])

interval_map = {
    "1m": "1m",
    "5m": "5m",
    "15m": "15m",
    "1h": "60m",
    "1d": "1d",
}
yf_interval = interval_map[ui_interval]

period_map = {
    "1m": "7d",
    "5m": "60d",
    "15m": "60d",
    "1h": "730d",
    "1d": "1y",
}
period = period_map[ui_interval]

chart_type = st.sidebar.radio(
    "Chart Mode",
    ["Basic Candlestick", "Advanced Candlestick + Pattern Tags"],
)

show_volume = st.sidebar.checkbox("Show Volume", value=False)
show_ma20 = st.sidebar.checkbox("Show MA20", value=True)
show_ma50 = st.sidebar.checkbox("Show MA50", value=False)


# -----------------------------
# Helpers
# -----------------------------
@st.cache_data(ttl=300, show_spinner=False)
def load_data(ticker_symbol: str, history_period: str, history_interval: str) -> pd.DataFrame:
    ticker = yf.Ticker(ticker_symbol)
    data = ticker.history(period=history_period, interval=history_interval)

    if data.empty:
        return data

    data = data.copy()
    data.index = pd.to_datetime(data.index)
    return data


def detect_patterns(row: pd.Series) -> str:
    o = row["Open"]
    h = row["High"]
    l = row["Low"]
    c = row["Close"]

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
        return "Hammer" if c >= o else "Hanging Man"
    if body_ratio > 0.2 and upper_ratio > 0.5 and lower_ratio < 0.2:
        return "Inverted Hammer" if c >= o else "Shooting Star"
    if c > o and body_ratio > 0.5:
        return "Bullish Candle"
    if o > c and body_ratio > 0.5:
        return "Bearish Candle"

    return ""


def filter_by_date(df: pd.DataFrame, selected_range) -> pd.DataFrame:
    if df.empty:
        return df

    if not isinstance(selected_range, (list, tuple)) or len(selected_range) != 2:
        return df

    start_date = pd.Timestamp(selected_range[0])
    end_date = pd.Timestamp(selected_range[1]) + pd.Timedelta(days=1)

    if df.index.tz is not None:
        start_date = start_date.tz_localize(df.index.tz)
        end_date = end_date.tz_localize(df.index.tz)

    return df[(df.index >= start_date) & (df.index < end_date)]


# -----------------------------
# Data load
# -----------------------------
st.write(f"Loading **{symbol_label}** with timeframe **{ui_interval}**...")

hist = load_data(symbol, period, yf_interval)

if hist.empty and ui_interval != "1d":
    st.warning("⚠️ No intraday data available for the selected interval. Falling back to daily candles.")
    ui_interval = "1d"
    yf_interval = "1d"
    period = "1y"
    hist = load_data(symbol, period, yf_interval)

if hist.empty:
    st.error("❌ No data available for this instrument and timeframe.")
    st.stop()

default_end = pd.Timestamp.today().date()
default_start = (pd.Timestamp.today() - pd.Timedelta(days=30)).date()

date_range = st.sidebar.date_input(
    "Date Range",
    value=(default_start, default_end),
)

hist = filter_by_date(hist, date_range)

if hist.empty:
    st.warning("⚠️ No data available for the selected date range.")
    st.stop()

hist = hist.copy()

if show_ma20:
    hist["MA20"] = hist["Close"].rolling(20).mean()

if show_ma50:
    hist["MA50"] = hist["Close"].rolling(50).mean()

if chart_type == "Advanced Candlestick + Pattern Tags":
    hist["Pattern"] = hist.apply(detect_patterns, axis=1)
else:
    hist["Pattern"] = ""


# -----------------------------
# KPI row
# -----------------------------
latest_close = float(hist["Close"].iloc[-1])
first_close = float(hist["Close"].iloc[0])
price_change = latest_close - first_close
pct_change = (price_change / first_close * 100) if first_close != 0 else 0
period_high = float(hist["High"].max())
period_low = float(hist["Low"].min())

k1, k2, k3, k4 = st.columns(4)
k1.metric("Last Close", f"{latest_close:,.2f}")
k2.metric("Period Change", f"{price_change:,.2f}", f"{pct_change:.2f}%")
k3.metric("Period High", f"{period_high:,.2f}")
k4.metric("Period Low", f"{period_low:,.2f}")


# -----------------------------
# Context cards
# -----------------------------
left, right = st.columns([1.35, 1])

with left:
    st.markdown(
        """
        <div class="db-section-card">
            <h3 class="db-section-title">Market Review Context</h3>
            <p class="db-section-copy">
                This view is designed to support quick inspection of market structure, recent price movement,
                and indicator overlays across common trading instruments. It provides a visual analysis layer
                that complements the persisted ingestion, metric snapshot, and API surfaces in the main Django platform.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with right:
    st.markdown(
        f"""
        <div class="db-section-card">
            <h3 class="db-section-title">Current Selection</h3>
            <p class="db-section-copy"><strong>Instrument:</strong> {symbol_label}</p>
            <p class="db-section-copy"><strong>Yahoo Symbol:</strong> {symbol}</p>
            <p class="db-section-copy"><strong>Timeframe:</strong> {ui_interval}</p>
            <p class="db-section-copy"><strong>Rows in View:</strong> {len(hist)}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


# -----------------------------
# Build figure
# -----------------------------
st.subheader(f"Chart View — {symbol_label}")

fig = go.Figure()

fig.add_trace(
    go.Candlestick(
        x=hist.index,
        open=hist["Open"],
        high=hist["High"],
        low=hist["Low"],
        close=hist["Close"],
        name="Candlesticks",
        increasing_line_color="lime",
        decreasing_line_color="red",
        increasing_fillcolor="rgba(0,255,0,0.35)",
        decreasing_fillcolor="rgba(255,0,0,0.35)",
    )
)

if show_ma20 and "MA20" in hist.columns:
    fig.add_trace(
        go.Scatter(
            x=hist.index,
            y=hist["MA20"],
            mode="lines",
            name="MA20",
            line=dict(width=2),
        )
    )

if show_ma50 and "MA50" in hist.columns:
    fig.add_trace(
        go.Scatter(
            x=hist.index,
            y=hist["MA50"],
            mode="lines",
            name="MA50",
            line=dict(width=2),
        )
    )

if chart_type == "Advanced Candlestick + Pattern Tags":
    pattern_points = hist[hist["Pattern"] != ""]
    if not pattern_points.empty:
        fig.add_trace(
            go.Scatter(
                x=pattern_points.index,
                y=pattern_points["High"],
                mode="markers+text",
                marker=dict(color="yellow", size=9, symbol="star"),
                text=pattern_points["Pattern"],
                textposition="top center",
                name="Patterns",
            )
        )

if show_volume and "Volume" in hist.columns:
    fig.add_trace(
        go.Bar(
            x=hist.index,
            y=hist["Volume"],
            name="Volume",
            opacity=0.22,
        )
    )

fig.update_layout(
    template="plotly_dark",
    height=720,
    margin=dict(l=20, r=20, t=40, b=20),
    xaxis_rangeslider_visible=True,
    dragmode="pan",
    xaxis_title="Time",
    yaxis_title="Price",
    hovermode="x unified",
    legend_title_text="Series",
)

st.plotly_chart(fig, use_container_width=True)


# -----------------------------
# Data preview and notes
# -----------------------------
with st.expander("Show underlying data"):
    preview_cols = ["Open", "High", "Low", "Close", "Volume"]
    extra_cols = [col for col in ["MA20", "MA50", "Pattern"] if col in hist.columns]
    st.dataframe(hist[preview_cols + extra_cols].tail(30), use_container_width=True)

st.markdown(
    """
    <div class="db-section-card">
        <h3 class="db-section-title">How this supports the broader project</h3>
        <p class="db-section-copy">
            In the full DataBridge Market API project, the Streamlit dashboard acts as a lightweight
            analyst-facing surface alongside the Django operational console, ETL commands, normalized
            storage models, and read-only API endpoints. This helps demonstrate not just data ingestion,
            but also business-facing presentation and exploratory analytics delivery.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.caption(
    "✅ Tip: Use the mouse wheel to zoom, drag to pan, and adjust the date range from the sidebar."
)