from django.core.management.base import BaseCommand, CommandError

from market_ingestion.models import IngestionRun
from market_ingestion.services.metrics import compute_latest_metric_snapshot


class Command(BaseCommand):
    help = "Compute the latest metric snapshot for a symbol/timeframe/source."

    def add_arguments(self, parser):
        parser.add_argument(
            "--symbol",
            required=True,
            help="Symbol to compute metrics for, e.g. BTC-USD.",
        )
        parser.add_argument(
            "--timeframe",
            default="1h",
            help="Timeframe to compute metrics for, e.g. 1h.",
        )
        parser.add_argument(
            "--source",
            required=True,
            help="Source label to store with the metric snapshot, e.g. yfinance, ccxt, twelvedata.",
        )
        parser.add_argument(
            "--run-id",
            type=int,
            default=None,
            help="Optional IngestionRun ID to link as the source run.",
        )

    def handle(self, *args, **options):
        symbol = options["symbol"]
        timeframe = options["timeframe"]
        source = options["source"]
        run_id = options["run_id"]

        source_run = None

        if run_id is not None:
            try:
                source_run = IngestionRun.objects.get(pk=run_id)
            except IngestionRun.DoesNotExist as exc:
                raise CommandError(f"IngestionRun with id={run_id} does not exist.") from exc

        self.stdout.write("Starting metric computation...")
        self.stdout.write(f"Symbol: {symbol}")
        self.stdout.write(f"Timeframe: {timeframe}")
        self.stdout.write(f"Source: {source}")
        self.stdout.write(f"Run ID: {run_id if run_id is not None else 'None'}")

        try:
            if source_run is not None:
                snapshot = compute_latest_metric_snapshot(
                    symbol=symbol,
                    timeframe=timeframe,
                    source=source,
                    source_run=source_run,
                )
            else:
                snapshot = compute_latest_metric_snapshot(
                    symbol=symbol,
                    timeframe=timeframe,
                    source=source,
                )
        except Exception as exc:
            raise CommandError(f"Metric computation failed: {exc}") from exc

        self.stdout.write(self.style.SUCCESS("Metric computation completed successfully."))
        self.stdout.write(f"Snapshot ID: {getattr(snapshot, 'id', 'Unknown')}")
        self.stdout.write(f"Snapshot: {snapshot}")