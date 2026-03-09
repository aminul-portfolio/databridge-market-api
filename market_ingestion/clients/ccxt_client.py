from __future__ import annotations

from typing import Any

import ccxt
import pandas as pd


def fetch_ohlcv(
    symbol: str = "BTC/USDT",
    timeframe: str = "1h",
    limit: int = 100,
    exchange_id: str = "binance",
) -> list[dict[str, Any]]:
    exchange_class = getattr(ccxt, exchange_id)
    exchange = exchange_class({"enableRateLimit": True})

    try:
        rows = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
    finally:
        close_method = getattr(exchange, "close", None)
        if callable(close_method):
            close_method()

    bars: list[dict[str, Any]] = []

    for row in rows:
        if len(row) < 6:
            continue

        timestamp = pd.to_datetime(row[0], unit="ms", errors="coerce", utc=True)
        if pd.isna(timestamp):
            continue

        bars.append(
            {
                "timestamp": timestamp.to_pydatetime(),
                "open": row[1],
                "high": row[2],
                "low": row[3],
                "close": row[4],
                "volume": row[5],
                "raw_payload": {
                    "timestamp_ms": row[0],
                    "open": row[1],
                    "high": row[2],
                    "low": row[3],
                    "close": row[4],
                    "volume": row[5],
                    "exchange_id": exchange_id,
                },
            }
        )

    return bars


def fetch_ticker(
    symbol: str = "BTC/USDT",
    exchange_id: str = "binance",
) -> dict[str, Any]:
    exchange_class = getattr(ccxt, exchange_id)
    exchange = exchange_class({"enableRateLimit": True})

    try:
        return exchange.fetch_ticker(symbol)
    finally:
        close_method = getattr(exchange, "close", None)
        if callable(close_method):
            close_method()