from __future__ import annotations

from typing import Any

import pandas as pd
import yfinance as yf


def _to_utc_datetime(value) -> pd.Timestamp | None:
    if value is None:
        return None
    ts = pd.to_datetime(value, errors="coerce", utc=True)
    if pd.isna(ts):
        return None
    return ts


def fetch_ohlcv(
    symbol: str = "BTC-USD",
    period: str = "7d",
    interval: str = "1h",
    limit: int | None = None,
) -> list[dict[str, Any]]:
    ticker = yf.Ticker(symbol)
    hist = ticker.history(period=period, interval=interval).reset_index()

    if hist.empty:
        return []

    timestamp_col = "Datetime" if "Datetime" in hist.columns else "Date"
    hist[timestamp_col] = pd.to_datetime(hist[timestamp_col], errors="coerce", utc=True)

    if limit:
        hist = hist.tail(limit)

    bars: list[dict[str, Any]] = []

    for _, row in hist.iterrows():
        timestamp = _to_utc_datetime(row.get(timestamp_col))
        if timestamp is None:
            continue

        raw_payload = {}
        for col in hist.columns:
            value = row.get(col)
            if isinstance(value, pd.Timestamp):
                raw_payload[col] = value.isoformat()
            elif pd.isna(value):
                raw_payload[col] = None
            else:
                raw_payload[col] = value.item() if hasattr(value, "item") else value

        bars.append(
            {
                "timestamp": timestamp.to_pydatetime(),
                "open": row.get("Open"),
                "high": row.get("High"),
                "low": row.get("Low"),
                "close": row.get("Close"),
                "volume": row.get("Volume"),
                "raw_payload": raw_payload,
            }
        )

    return bars