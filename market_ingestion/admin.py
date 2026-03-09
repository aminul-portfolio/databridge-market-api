from django.contrib import admin
from .models import TradeLog, OHLCV, BacktestResult


@admin.register(TradeLog)
class TradeLogAdmin(admin.ModelAdmin):
    list_display = (
        "symbol",
        "open_time",
        "close_time",
        "open_price",
        "close_price",
        "volume",
        "pnl",
        "strategy",
    )
    list_filter = ("symbol", "strategy")
    search_fields = ("symbol", "strategy")
    date_hierarchy = "open_time"


@admin.register(OHLCV)
class OHLCVAdmin(admin.ModelAdmin):
    list_display = (
        "symbol",
        "timestamp",
        "open",
        "high",
        "low",
        "close",
        "volume",
    )
    list_filter = ("symbol",)
    search_fields = ("symbol",)
    date_hierarchy = "timestamp"


@admin.register(BacktestResult)
class BacktestResultAdmin(admin.ModelAdmin):
    list_display = (
        "symbol",
        "strategy",
        "timestamp",
    )
    list_filter = ("symbol", "strategy")
    search_fields = ("symbol", "strategy")
    date_hierarchy = "timestamp"
from django.contrib import admin

from .models import IngestionRun, MarketBar, MetricSnapshot, TradeJournalEntry


@admin.register(IngestionRun)
class IngestionRunAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "source",
        "symbol",
        "timeframe",
        "status",
        "rows_inserted",
        "rows_updated",
        "rows_skipped",
        "started_at",
        "finished_at",
    )
    list_filter = ("source", "status", "timeframe")
    search_fields = ("symbol", "error_message")
    ordering = ("-started_at",)


@admin.register(MarketBar)
class MarketBarAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "source",
        "symbol",
        "timeframe",
        "timestamp",
        "open",
        "high",
        "low",
        "close",
        "volume",
    )
    list_filter = ("source", "symbol", "timeframe")
    search_fields = ("symbol",)
    ordering = ("-timestamp",)


@admin.register(MetricSnapshot)
class MetricSnapshotAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "symbol",
        "timeframe",
        "snapshot_time",
        "close_price",
        "return_1d",
        "return_7d",
        "volatility_14d",
        "crossover_signal",
    )
    list_filter = ("symbol", "timeframe", "crossover_signal")
    search_fields = ("symbol",)
    ordering = ("-snapshot_time",)


@admin.register(TradeJournalEntry)
class TradeJournalEntryAdmin(admin.ModelAdmin):
    list_display = (
        "id",
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
    )
    list_filter = ("symbol", "side", "source_file")
    search_fields = ("symbol", "notes", "source_file")
    ordering = ("-opened_at", "-id")