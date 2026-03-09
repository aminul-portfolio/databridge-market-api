from __future__ import annotations

from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

import pandas as pd
from django.db import transaction
from django.utils import timezone

from market_ingestion.models import IngestionRun, TradeJournalEntry


def _first_value(row: dict[str, Any], candidates: list[str], default=None):
    for key in candidates:
        if key in row and row[key] not in ("", None):
            return row[key]
    return default


def _to_decimal(value):
    if value in ("", None):
        return None
    try:
        return Decimal(str(value).replace(",", ""))
    except (InvalidOperation, TypeError, ValueError):
        return None


def _to_datetime(value):
    if value in ("", None):
        return None
    dt = pd.to_datetime(value, errors="coerce", utc=True)
    if pd.isna(dt):
        return None
    return dt.to_pydatetime()


@transaction.atomic
def import_trade_journal_csv(file_path: str | Path) -> IngestionRun:
    path = Path(file_path)

    run = IngestionRun.objects.create(
        source="journal_csv",
        symbol="MULTI",
        timeframe="",
        status="started",
        metadata={"file_path": str(path)},
    )

    if not path.exists():
        run.status = "failed"
        run.finished_at = timezone.now()
        run.error_message = f"File not found: {path}"
        run.save(update_fields=["status", "finished_at", "error_message"])
        return run

    inserted = 0
    updated = 0
    skipped = 0

    try:
        df = pd.read_csv(path)
        records = df.to_dict(orient="records")

        for idx, row in enumerate(records, start=1):
            symbol = _first_value(row, ["Symbol", "symbol", "Pair", "Instrument"], default="UNKNOWN")
            side = _first_value(row, ["Side", "Type", "side"], default="")
            opened_at = _to_datetime(_first_value(row, ["Open", "Open Time", "Opened At", "Entry Time"]))
            closed_at = _to_datetime(_first_value(row, ["Close Time", "Closed At", "Exit Time"]))
            open_price = _to_decimal(_first_value(row, ["Open Price", "Open price", "Entry", "Entry Price"]))
            close_price = _to_decimal(_first_value(row, ["Close Price", "Close price", "Exit", "Exit Price"]))
            size = _to_decimal(_first_value(row, ["Size", "Volume", "Lots", "Quantity"]))
            pnl = _to_decimal(_first_value(row, ["PnL", "P/L", "Profit", "Net Profit"]))
            notes = _first_value(row, ["Notes", "Comment", "comments"], default="")

            obj, created = TradeJournalEntry.objects.update_or_create(
                source_file=path.name,
                row_number=idx,
                defaults={
                    "symbol": symbol,
                    "side": side,
                    "opened_at": opened_at,
                    "closed_at": closed_at,
                    "open_price": open_price,
                    "close_price": close_price,
                    "size": size,
                    "pnl": pnl,
                    "notes": notes or "",
                    "raw_row": row,
                    "ingestion_run": run,
                },
            )

            if created:
                inserted += 1
            else:
                updated += 1

        run.status = "success"
        run.rows_inserted = inserted
        run.rows_updated = updated
        run.rows_skipped = skipped
        run.finished_at = timezone.now()
        run.save(
            update_fields=[
                "status",
                "rows_inserted",
                "rows_updated",
                "rows_skipped",
                "finished_at",
            ]
        )
        return run

    except Exception as exc:
        run.status = "failed"
        run.rows_inserted = inserted
        run.rows_updated = updated
        run.rows_skipped = skipped
        run.finished_at = timezone.now()
        run.error_message = str(exc)
        run.save(
            update_fields=[
                "status",
                "rows_inserted",
                "rows_updated",
                "rows_skipped",
                "finished_at",
                "error_message",
            ]
        )
        return run