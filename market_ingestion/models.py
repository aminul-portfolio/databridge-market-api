from django.db import models



class TradeLog(models.Model):
    symbol = models.CharField(max_length=20)
    open_time = models.DateTimeField()
    close_time = models.DateTimeField(null=True, blank=True)
    open_price = models.DecimalField(max_digits=20, decimal_places=8)
    close_price = models.DecimalField(max_digits=20, decimal_places=8, null=True, blank=True)
    volume = models.DecimalField(max_digits=20, decimal_places=8, null=True, blank=True)
    pnl = models.DecimalField("Profit/Loss", max_digits=20, decimal_places=8, null=True, blank=True)
    strategy = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f"{self.symbol} trade on {self.open_time.strftime('%Y-%m-%d %H:%M')}"


class OHLCV(models.Model):
    symbol = models.CharField(max_length=20)
    timestamp = models.DateTimeField()
    open = models.DecimalField(max_digits=20, decimal_places=8)
    high = models.DecimalField(max_digits=20, decimal_places=8)
    low = models.DecimalField(max_digits=20, decimal_places=8)
    close = models.DecimalField(max_digits=20, decimal_places=8)
    volume = models.DecimalField(max_digits=20, decimal_places=8)

    class Meta:
        unique_together = ('symbol', 'timestamp')
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.symbol} {self.timestamp.strftime('%Y-%m-%d %H:%M')}"


class BacktestResult(models.Model):
    symbol = models.CharField(max_length=20)
    strategy = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now_add=True)
    params = models.TextField(help_text="JSON or text of strategy parameters")
    results_json = models.TextField(help_text="Backtest results stored as JSON")

    def __str__(self):
        return f"{self.symbol} {self.strategy} ({self.timestamp.strftime('%Y-%m-%d')})"



SOURCE_CHOICES = [
    ("yfinance", "yfinance"),
    ("ccxt", "ccxt"),
    ("twelvedata", "TwelveData"),
    ("journal_csv", "Journal CSV"),
]

RUN_STATUS_CHOICES = [
    ("started", "Started"),
    ("success", "Success"),
    ("partial", "Partial"),
    ("failed", "Failed"),
]

SIGNAL_CHOICES = [
    ("bullish", "Bullish"),
    ("bearish", "Bearish"),
    ("neutral", "Neutral"),
]


class IngestionRun(models.Model):
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES)
    symbol = models.CharField(max_length=32)
    timeframe = models.CharField(max_length=16, blank=True, default="")
    status = models.CharField(max_length=20, choices=RUN_STATUS_CHOICES, default="started")

    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)

    rows_inserted = models.PositiveIntegerField(default=0)
    rows_updated = models.PositiveIntegerField(default=0)
    rows_skipped = models.PositiveIntegerField(default=0)

    error_message = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-started_at"]
        indexes = [
            models.Index(fields=["source", "symbol", "timeframe"]),
            models.Index(fields=["status", "started_at"]),
        ]

    def __str__(self):
        label = f"{self.source}:{self.symbol}"
        if self.timeframe:
            label = f"{label}:{self.timeframe}"
        return f"{label} [{self.status}]"


class MarketBar(models.Model):
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES)
    symbol = models.CharField(max_length=32)
    timeframe = models.CharField(max_length=16, default="1h")
    timestamp = models.DateTimeField()

    open = models.DecimalField(max_digits=20, decimal_places=8)
    high = models.DecimalField(max_digits=20, decimal_places=8)
    low = models.DecimalField(max_digits=20, decimal_places=8)
    close = models.DecimalField(max_digits=20, decimal_places=8)
    volume = models.DecimalField(max_digits=24, decimal_places=8, null=True, blank=True)

    ingestion_run = models.ForeignKey(
        IngestionRun,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="market_bars",
    )
    raw_payload = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-timestamp"]
        constraints = [
            models.UniqueConstraint(
                fields=["source", "symbol", "timeframe", "timestamp"],
                name="unique_marketbar_per_source_symbol_timeframe_timestamp",
            )
        ]
        indexes = [
            models.Index(fields=["symbol", "timeframe", "timestamp"]),
            models.Index(fields=["source", "symbol", "timestamp"]),
        ]

    def __str__(self):
        return f"{self.symbol} {self.timeframe} @ {self.timestamp}"


class MetricSnapshot(models.Model):
    symbol = models.CharField(max_length=32)
    timeframe = models.CharField(max_length=16, default="1h")
    snapshot_time = models.DateTimeField()

    close_price = models.DecimalField(max_digits=20, decimal_places=8)
    return_1d = models.DecimalField(max_digits=20, decimal_places=8, null=True, blank=True)
    return_7d = models.DecimalField(max_digits=20, decimal_places=8, null=True, blank=True)
    volatility_14d = models.DecimalField(max_digits=20, decimal_places=8, null=True, blank=True)

    sma_fast = models.DecimalField(max_digits=20, decimal_places=8, null=True, blank=True)
    sma_slow = models.DecimalField(max_digits=20, decimal_places=8, null=True, blank=True)
    crossover_signal = models.CharField(
        max_length=16,
        choices=SIGNAL_CHOICES,
        default="neutral",
    )

    source_run = models.ForeignKey(
        IngestionRun,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="metric_snapshots",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-snapshot_time"]
        constraints = [
            models.UniqueConstraint(
                fields=["symbol", "timeframe", "snapshot_time"],
                name="unique_metricsnapshot_per_symbol_timeframe_snapshot",
            )
        ]
        indexes = [
            models.Index(fields=["symbol", "timeframe", "snapshot_time"]),
        ]

    def __str__(self):
        return f"{self.symbol} {self.timeframe} metrics @ {self.snapshot_time}"


class TradeJournalEntry(models.Model):
    symbol = models.CharField(max_length=32)
    side = models.CharField(max_length=16, blank=True, default="")

    opened_at = models.DateTimeField(null=True, blank=True)
    closed_at = models.DateTimeField(null=True, blank=True)

    open_price = models.DecimalField(max_digits=20, decimal_places=8, null=True, blank=True)
    close_price = models.DecimalField(max_digits=20, decimal_places=8, null=True, blank=True)
    size = models.DecimalField(max_digits=20, decimal_places=8, null=True, blank=True)
    pnl = models.DecimalField(max_digits=20, decimal_places=8, null=True, blank=True)

    source_file = models.CharField(max_length=255, default="trading-journal.csv")
    row_number = models.PositiveIntegerField()

    notes = models.TextField(blank=True)
    raw_row = models.JSONField(default=dict, blank=True)

    ingestion_run = models.ForeignKey(
        IngestionRun,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="journal_entries",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-opened_at", "-id"]
        constraints = [
            models.UniqueConstraint(
                fields=["source_file", "row_number"],
                name="unique_tradejournalentry_per_file_row",
            )
        ]
        indexes = [
            models.Index(fields=["symbol", "opened_at"]),
            models.Index(fields=["source_file", "row_number"]),
        ]

    def __str__(self):
        return f"{self.symbol} row {self.row_number} ({self.source_file})"