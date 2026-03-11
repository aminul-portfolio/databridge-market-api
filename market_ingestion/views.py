import base64
import json
from io import BytesIO

import ccxt
import ccxt.async_support as ccxt_async
import matplotlib.pyplot as plt
import pandas as pd
import requests
import yfinance as yf
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render

from .models import IngestionRun, MarketBar, MetricSnapshot, TradeJournalEntry


def _to_pretty_json(data):
    return json.dumps(data, indent=2, default=str)


def _normalize_dataframe_for_template(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df

    df = df.copy()

    for col in df.columns:
        if (
            pd.api.types.is_datetime64_any_dtype(df[col])
            or pd.api.types.is_datetime64tz_dtype(df[col])
        ):
            df[col] = df[col].astype(str)

    return df


def _safe_close_exchange(exchange) -> None:
    close_method = getattr(exchange, "close", None)
    if callable(close_method):
        close_method()


def _fetch_btc_yfinance_history(limit: int = 50, period: str = "7d", interval: str = "1h") -> pd.DataFrame:
    ticker = yf.Ticker("BTC-USD")
    hist = ticker.history(period=period, interval=interval).reset_index()
    hist = _normalize_dataframe_for_template(hist)
    return hist.tail(limit)


def _fetch_raw_btc_yfinance_history(period: str = "7d", interval: str = "1h") -> pd.DataFrame:
    ticker = yf.Ticker("BTC-USD")
    return ticker.history(period=period, interval=interval).reset_index()


def _fetch_btc_ccxt_ticker() -> dict:
    exchange = ccxt.binance({"enableRateLimit": True})
    try:
        return exchange.fetch_ticker("BTC/USDT")
    finally:
        _safe_close_exchange(exchange)


def _fetch_eurusd_twelvedata(outputsize: int = 50) -> dict:
    if not settings.TWELVEDATA_API_KEY:
        return {
            "status": "error",
            "message": "TWELVEDATA_API_KEY is not configured.",
        }

    url = "https://api.twelvedata.com/time_series"
    params = {
        "symbol": "EUR/USD",
        "interval": "1h",
        "outputsize": outputsize,
        "apikey": settings.TWELVEDATA_API_KEY,
    }

    try:
        response = requests.get(url, params=params, timeout=20)
        response.raise_for_status()
        data = response.json()

        if data.get("status") == "error":
            if data.get("code") == 401:
                return {
                    "status": "error",
                    "message": "TwelveData authentication failed. The API key is invalid, inactive, or not accepted by TwelveData.",
                }
            return {
                "status": "error",
                "message": data.get("message", "TwelveData returned an error."),
            }

        return data

    except requests.RequestException as exc:
        return {
            "status": "error",
            "message": f"Failed to fetch TwelveData: {exc}",
        }


def _twelvedata_to_records(data_td: dict) -> list[dict]:
    if "values" not in data_td:
        return [{"error": data_td.get("message", "Error fetching data")}]

    df_td = pd.json_normalize(data_td["values"])

    if "datetime" in df_td.columns:
        df_td["datetime"] = pd.to_datetime(df_td["datetime"], errors="coerce")

    numeric_cols = [col for col in ["open", "high", "low", "close", "volume"] if col in df_td.columns]
    if numeric_cols:
        df_td[numeric_cols] = df_td[numeric_cols].apply(pd.to_numeric, errors="coerce")

    df_td = _normalize_dataframe_for_template(df_td)
    return df_td.to_dict(orient="records")


def home(request):
    latest_run = IngestionRun.objects.order_by("-id").first()
    latest_successful_run = IngestionRun.objects.filter(status="success").order_by("-id").first()
    latest_snapshot = MetricSnapshot.objects.order_by("-id").first()

    context = {
        "total_runs": IngestionRun.objects.count(),
        "total_bars": MarketBar.objects.count(),
        "total_snapshots": MetricSnapshot.objects.count(),
        "total_journal_entries": TradeJournalEntry.objects.count(),
        "latest_run": latest_run,
        "latest_successful_run": latest_successful_run,
        "latest_snapshot": latest_snapshot,
        "recent_runs": IngestionRun.objects.order_by("-id")[:5],
    }
    return render(request, "home.html", context)


def btc_yfinance(request):
    try:
        data = _fetch_btc_yfinance_history(limit=50).to_dict(orient="records")
        pretty_json = _to_pretty_json(data)
    except Exception as exc:
        pretty_json = _to_pretty_json({"error": f"Failed to fetch BTC yfinance data: {exc}"})

    return render(
        request,
        "json_view.html",
        {
            "title": "BTC/USD yfinance JSON",
            "json_data": pretty_json,
        },
    )


def btc_yfinance_page(request):
    try:
        data = _fetch_btc_yfinance_history(limit=50).to_dict(orient="records")
    except Exception as exc:
        data = [{"error": f"Failed to fetch BTC yfinance data: {exc}"}]

    return render(
        request,
        "table.html",
        {
            "title": "BTC/USD yfinance Table",
            "data": data,
        },
    )


def btc_ccxt(request):
    try:
        ticker = _fetch_btc_ccxt_ticker()
        pretty_json = _to_pretty_json(ticker)
    except Exception as exc:
        pretty_json = _to_pretty_json({"error": f"Failed to fetch BTC ccxt data: {exc}"})

    return render(
        request,
        "json_view.html",
        {
            "title": "BTC/USDT ccxt JSON",
            "json_data": pretty_json,
        },
    )


def btc_ccxt_page(request):
    try:
        ticker = _fetch_btc_ccxt_ticker()
        data = [ticker]
    except Exception as exc:
        data = [{"error": f"Failed to fetch BTC ccxt data: {exc}"}]

    return render(
        request,
        "table.html",
        {
            "title": "BTC/USDT ccxt Table",
            "data": data,
        },
    )


def eurusd_twelvedata_page(request):
    data_td = _fetch_eurusd_twelvedata(outputsize=50)
    eurusd_data = _twelvedata_to_records(data_td)

    return render(
        request,
        "table.html",
        {
            "title": "EUR/USD TwelveData Table",
            "data": eurusd_data,
        },
    )


def eurusd_twelvedata_json(request):
    data_td = _fetch_eurusd_twelvedata(outputsize=50)

    return render(
        request,
        "json_view.html",
        {
            "title": "EUR/USD TwelveData JSON",
            "json_data": _to_pretty_json(data_td),
        },
    )


def btc_yfinance_info(request):
    try:
        ticker = yf.Ticker("BTC-USD")
        info = ticker.info or {}
        selected_info = {
            "Market Cap": info.get("marketCap", "Unknown"),
            "Sector": info.get("sector", "Unknown"),
            "Currency": info.get("currency", "Unknown"),
            "Quote Type": info.get("quoteType", "Unknown"),
        }
    except Exception as exc:
        selected_info = {"error": f"Failed to fetch BTC market info: {exc}"}

    return render(
        request,
        "info_view.html",
        {
            "title": "BTC/USD Market Info",
            "info": selected_info,
        },
    )


def btc_yfinance_compare(request):
    try:
        journal_qs = (
            TradeJournalEntry.objects.filter(
                symbol__icontains="BTC",
                opened_at__isnull=False,
            )
            .order_by("opened_at", "id")
            .values(
                "symbol",
                "side",
                "opened_at",
                "closed_at",
                "open_price",
                "close_price",
                "size",
                "pnl",
                "source_file",
                "row_number",
                "notes",
            )
        )

        journal_rows = list(journal_qs)

        if not journal_rows:
            return render(
                request,
                "table.html",
                {
                    "title": "Trade Log Comparison",
                    "data": [{"info": "No BTC trade journal entries available for comparison."}],
                },
            )

        trades = pd.DataFrame(journal_rows)

        trades["opened_at"] = pd.to_datetime(trades["opened_at"], utc=True, errors="coerce")
        trades["closed_at"] = pd.to_datetime(trades["closed_at"], utc=True, errors="coerce")

        numeric_cols = ["open_price", "close_price", "size", "pnl"]
        for col in numeric_cols:
            if col in trades.columns:
                trades[col] = pd.to_numeric(trades[col], errors="coerce")

        trades = trades.dropna(subset=["opened_at"]).sort_values("opened_at")

        hist = _fetch_raw_btc_yfinance_history(period="7d", interval="1h")

        datetime_col = "Datetime" if "Datetime" in hist.columns else "Date"
        hist[datetime_col] = pd.to_datetime(hist[datetime_col], utc=True, errors="coerce")
        hist = hist.dropna(subset=[datetime_col]).sort_values(datetime_col)

        merged = pd.merge_asof(
            trades,
            hist,
            left_on="opened_at",
            right_on=datetime_col,
            direction="nearest",
        )

        if "Close" in merged.columns and "open_price" in merged.columns:
            merged["market_vs_trade_open_diff"] = merged["Close"] - merged["open_price"]

        merged = _normalize_dataframe_for_template(merged)
        data = merged.to_dict(orient="records")

    except Exception as exc:
        data = [{"error": f"Failed to compare trade journal with BTC data: {exc}"}]

    return render(
        request,
        "table.html",
        {
            "title": "Trade Log Comparison",
            "data": data,
        },
    )


def btc_yfinance_plot(request):
    try:
        hist = yf.Ticker("BTC-USD").history(period="7d", interval="1h")

        plt.figure(figsize=(10, 5))
        plt.plot(hist.index, hist["Close"], marker="o", linestyle="-")
        plt.title("BTC/USD Closing Prices")
        plt.xlabel("Date")
        plt.ylabel("Price (USD)")
        plt.xticks(rotation=45)
        plt.grid(True)
        plt.tight_layout()

        buf = BytesIO()
        plt.savefig(buf, format="png")
        plt.close()
        buf.seek(0)
        image_base64 = base64.b64encode(buf.read()).decode("utf-8")
        buf.close()
    except Exception as exc:
        return render(
            request,
            "info_view.html",
            {
                "title": "BTC/USD Chart",
                "info": {"error": f"Failed to generate BTC chart: {exc}"},
            },
        )

    return render(
        request,
        "plot_view.html",
        {
            "title": "BTC/USD Chart",
            "chart_base64": image_base64,
        },
    )


# Legacy / non-primary demo views kept in code for reference,
# but intentionally excluded from the public demo namespace
# and recruiter-facing navigation.

def eth_ohlcv(request):
    exchange = None
    try:
        exchange = ccxt.binance({"enableRateLimit": True})
        ohlcv = exchange.fetch_ohlcv("ETH/USDT", "1h", limit=50)
        df = pd.DataFrame(ohlcv, columns=["timestamp", "open", "high", "low", "close", "volume"])
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms", errors="coerce")
        df = _normalize_dataframe_for_template(df)
        data = df.to_dict(orient="records")
    except Exception as exc:
        data = [{"error": f"Failed to fetch ETH OHLCV data: {exc}"}]
    finally:
        if exchange is not None:
            _safe_close_exchange(exchange)

    return render(
        request,
        "table.html",
        {
            "title": "ETH/USDT OHLCV",
            "data": data,
        },
    )


def eth_backtest(request):
    exchange = None
    try:
        exchange = ccxt.binance({"enableRateLimit": True})
        ohlcv = exchange.fetch_ohlcv("ETH/USDT", "1h", limit=200)
        df = pd.DataFrame(ohlcv, columns=["timestamp", "open", "high", "low", "close", "volume"])
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms", errors="coerce")
        df["sma_fast"] = df["close"].rolling(5).mean()
        df["sma_slow"] = df["close"].rolling(20).mean()
        df["signal"] = (df["sma_fast"] > df["sma_slow"]).astype(int)
        df = _normalize_dataframe_for_template(df)
        data = df.tail(20).to_dict(orient="records")
    except Exception as exc:
        data = [{"error": f"Failed to run ETH SMA backtest: {exc}"}]
    finally:
        if exchange is not None:
            _safe_close_exchange(exchange)

    return render(
        request,
        "table.html",
        {
            "title": "ETH SMA Backtest",
            "data": data,
        },
    )


def btc_volatility(request):
    try:
        tickers = yf.download(
            tickers=["BTC-USD", "ETH-USD"],
            period="6mo",
            interval="1d",
            group_by="ticker",
            auto_adjust=True,
        )
        btc_close = tickers["BTC-USD"]["Close"]
        returns = btc_close.pct_change()
        volatility = returns.rolling(14).std() * (252 ** 0.5)

        data = {
            "dates": btc_close.index.strftime("%Y-%m-%d").tolist(),
            "volatility": volatility.fillna(0).tolist(),
        }
        return JsonResponse(data)
    except Exception as exc:
        return JsonResponse(
            {"error": f"Failed to calculate BTC volatility: {exc}"},
            status=500,
        )


async def ccxt_async_ticker(request):
    symbol = request.GET.get("symbol", "BTC/USDT")
    exchange = ccxt_async.binance({"enableRateLimit": True})

    try:
        ticker = await exchange.fetch_ticker(symbol)
        return JsonResponse(ticker)
    except Exception as exc:
        return JsonResponse(
            {"error": f"Failed to fetch async ticker for {symbol}: {exc}"},
            status=500,
        )
    finally:
        await exchange.close()

def public_landing(request):
    context = {
        "total_runs": IngestionRun.objects.count(),
        "total_bars": MarketBar.objects.count(),
        "total_snapshots": MetricSnapshot.objects.count(),
        "total_journal_entries": TradeJournalEntry.objects.count(),
        "latest_run": IngestionRun.objects.order_by("-id").first(),
        "latest_snapshot": MetricSnapshot.objects.order_by("-id").first(),
        "streamlit_url": getattr(settings, "STREAMLIT_URL", ""),
        "github_url": "https://github.com/aminul-portfolio/databridge-market-api",
    }
    return render(request, "public_landing.html", context)