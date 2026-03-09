from __future__ import annotations

from decimal import Decimal, InvalidOperation
from typing import Any

from django.db import transaction
from django.utils import timezone

from market_ingestion.clients import ccxt_client, twelvedata_client, yfinance_client
from market_ingestion.models import IngestionRun, MarketBar


def _to_decimal(value) -> Decimal | None:
    if value is None or value == "":
        return None
    try:
        return Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return None


def _finalize_run(
    run: IngestionRun,
    *,
    status: str,
    rows_inserted: int | None = None,
    rows_updated: int | None = None,
    rows_skipped: int | None = None,
    error_message: str = "",
) -> IngestionRun:
    run.status = status
    run.finished_at = timezone.now()

    if rows_inserted is not None:
        run.rows_inserted = rows_inserted
    if rows_updated is not None:
        run.rows_updated = rows_updated
    if rows_skipped is not None:
        run.rows_skipped = rows_skipped

    run.error_message = error_message
    run.save(
        update_fields=[
            "status",
            "finished_at",
            "rows_inserted",
            "rows_updated",
            "rows_skipped",
            "error_message",
        ]
    )
    return run


@transaction.atomic
def ingest_market_bars(
    *,
    source: str,
    symbol: str,
    timeframe: str,
    bars: list[dict[str, Any]],
    metadata: dict[str, Any] | None = None,
) -> IngestionRun:
    metadata = metadata or {}

    run = IngestionRun.objects.create(
        source=source,
        symbol=symbol,
        timeframe=timeframe,
        status="started",
        metadata=metadata,
    )

    inserted = 0
    updated = 0
    skipped = 0

    try:
        for bar in bars:
            timestamp = bar.get("timestamp")
            open_price = _to_decimal(bar.get("open"))
            high_price = _to_decimal(bar.get("high"))
            low_price = _to_decimal(bar.get("low"))
            close_price = _to_decimal(bar.get("close"))
            volume = _to_decimal(bar.get("volume"))
            raw_payload = bar.get("raw_payload", {})

            if not timestamp or open_price is None or high_price is None or low_price is None or close_price is None:
                skipped += 1
                continue

            obj, created = MarketBar.objects.update_or_create(
                source=source,
                symbol=symbol,
                timeframe=timeframe,
                timestamp=timestamp,
                defaults={
                    "open": open_price,
                    "high": high_price,
                    "low": low_price,
                    "close": close_price,
                    "volume": volume,
                    "ingestion_run": run,
                    "raw_payload": raw_payload,
                },
            )

            if created:
                inserted += 1
            else:
                updated += 1

        status = "success" if (inserted or updated) and skipped == 0 else "partial"
        return _finalize_run(
            run,
            status=status,
            rows_inserted=inserted,
            rows_updated=updated,
            rows_skipped=skipped,
        )

    except Exception as exc:
        return _finalize_run(
            run,
            status="failed",
            rows_inserted=inserted,
            rows_updated=updated,
            rows_skipped=skipped,
            error_message=str(exc),
        )


def ingest_from_yfinance(
    *,
    symbol: str = "BTC-USD",
    timeframe: str = "1h",
    period: str = "7d",
    limit: int = 100,
) -> IngestionRun:
    bars = yfinance_client.fetch_ohlcv(
        symbol=symbol,
        period=period,
        interval=timeframe,
        limit=limit,
    )
    return ingest_market_bars(
        source="yfinance",
        symbol=symbol,
        timeframe=timeframe,
        bars=bars,
        metadata={"period": period, "provider": "yfinance"},
    )


def ingest_from_ccxt(
    *,
    symbol: str = "BTC/USDT",
    timeframe: str = "1h",
    limit: int = 100,
    exchange_id: str = "binance",
) -> IngestionRun:
    bars = ccxt_client.fetch_ohlcv(
        symbol=symbol,
        timeframe=timeframe,
        limit=limit,
        exchange_id=exchange_id,
    )
    return ingest_market_bars(
        source="ccxt",
        symbol=symbol,
        timeframe=timeframe,
        bars=bars,
        metadata={"exchange_id": exchange_id, "provider": "ccxt"},
    )


def ingest_from_twelvedata(
    *,
    symbol: str = "EUR/USD",
    timeframe: str = "1h",
    outputsize: int = 100,
) -> IngestionRun:
    bars = twelvedata_client.fetch_ohlcv(
        symbol=symbol,
        interval=timeframe,
        outputsize=outputsize,
    )
    return ingest_market_bars(
        source="twelvedata",
        symbol=symbol,
        timeframe=timeframe,
        bars=bars,
        metadata={"provider": "twelvedata"},
    )