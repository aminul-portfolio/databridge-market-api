from __future__ import annotations

from typing import Any

import pandas as pd
import requests
from django.conf import settings


class TwelveDataClientError(Exception):
    pass


def fetch_time_series(
    symbol: str = "EUR/USD",
    interval: str = "1h",
    outputsize: int = 100,
) -> dict[str, Any]:
    if not settings.TWELVEDATA_API_KEY:
        raise TwelveDataClientError("TWELVEDATA_API_KEY is not configured.")

    url = "https://api.twelvedata.com/time_series"
    params = {
        "symbol": symbol,
        "interval": interval,
        "outputsize": outputsize,
        "apikey": settings.TWELVEDATA_API_KEY,
    }

    response = requests.get(url, params=params, timeout=20)
    response.raise_for_status()
    data = response.json()

    if data.get("status") == "error":
        raise TwelveDataClientError(data.get("message", "TwelveData returned an error."))

    return data


def fetch_ohlcv(
    symbol: str = "EUR/USD",
    interval: str = "1h",
    outputsize: int = 100,
) -> list[dict[str, Any]]:
    data = fetch_time_series(symbol=symbol, interval=interval, outputsize=outputsize)
    values = data.get("values", [])

    bars: list[dict[str, Any]] = []

    for row in values:
        timestamp = pd.to_datetime(row.get("datetime"), errors="coerce", utc=True)
        if pd.isna(timestamp):
            continue

        bars.append(
            {
                "timestamp": timestamp.to_pydatetime(),
                "open": row.get("open"),
                "high": row.get("high"),
                "low": row.get("low"),
                "close": row.get("close"),
                "volume": row.get("volume"),
                "raw_payload": row,
            }
        )

    bars.sort(key=lambda item: item["timestamp"])
    return bars