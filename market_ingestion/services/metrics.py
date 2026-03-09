from __future__ import annotations

from decimal import Decimal, InvalidOperation

import pandas as pd

from market_ingestion.models import IngestionRun, MarketBar, MetricSnapshot


def _to_decimal(value):
    if value is None or pd.isna(value):
        return None
    try:
        return Decimal(str(round(float(value), 8)))
    except (InvalidOperation, TypeError, ValueError):
        return None


def _periods_per_day(timeframe: str) -> int:
    mapping = {
        "1h": 24,
        "4h": 6,
        "1d": 1,
    }
    return mapping.get(timeframe, 24)


def _periods_per_year(timeframe: str) -> int:
    mapping = {
        "1h": 24 * 365,
        "4h": 6 * 365,
        "1d": 365,
    }
    return mapping.get(timeframe, 24 * 365)


def compute_latest_metric_snapshot(
    *,
    symbol: str,
    timeframe: str = "1h",
    source: str | None = None,
    source_run: IngestionRun | None = None,
) -> MetricSnapshot | None:
    qs = MarketBar.objects.filter(symbol=symbol, timeframe=timeframe).order_by("timestamp")

    if source:
        qs = qs.filter(source=source)

    rows = list(qs.values("timestamp", "close"))
    if not rows:
        return None

    df = pd.DataFrame(rows)
    if df.empty:
        return None

    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce", utc=True)
    df["close"] = pd.to_numeric(df["close"], errors="coerce")
    df = df.dropna(subset=["timestamp", "close"]).sort_values("timestamp")

    if df.empty:
        return None

    periods_day = _periods_per_day(timeframe)
    periods_year = _periods_per_year(timeframe)

    df["returns"] = df["close"].pct_change()
    df["return_1d"] = (df["close"] / df["close"].shift(periods_day)) - 1
    df["return_7d"] = (df["close"] / df["close"].shift(periods_day * 7)) - 1
    df["volatility_14d"] = df["returns"].rolling(periods_day * 14).std() * (periods_year ** 0.5)

    df["sma_fast"] = df["close"].rolling(5).mean()
    df["sma_slow"] = df["close"].rolling(20).mean()

    last = df.iloc[-1]

    signal = "neutral"
    sma_fast = last.get("sma_fast")
    sma_slow = last.get("sma_slow")

    if pd.notna(sma_fast) and pd.notna(sma_slow):
        if sma_fast > sma_slow:
            signal = "bullish"
        elif sma_fast < sma_slow:
            signal = "bearish"

    snapshot, _ = MetricSnapshot.objects.update_or_create(
        symbol=symbol,
        timeframe=timeframe,
        snapshot_time=last["timestamp"].to_pydatetime(),
        defaults={
            "close_price": _to_decimal(last["close"]),
            "return_1d": _to_decimal(last.get("return_1d")),
            "return_7d": _to_decimal(last.get("return_7d")),
            "volatility_14d": _to_decimal(last.get("volatility_14d")),
            "sma_fast": _to_decimal(sma_fast),
            "sma_slow": _to_decimal(sma_slow),
            "crossover_signal": signal,
            "source_run": source_run,
        },
    )

    return snapshot