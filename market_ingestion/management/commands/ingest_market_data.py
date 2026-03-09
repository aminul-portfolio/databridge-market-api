from django.core.management.base import BaseCommand, CommandError

from market_ingestion.services.ingestion import (
    ingest_from_ccxt,
    ingest_from_twelvedata,
    ingest_from_yfinance,
)


class Command(BaseCommand):
    help = "Ingest market data from yfinance, ccxt, or TwelveData into normalized models."

    def add_arguments(self, parser):
        parser.add_argument(
            "--source",
            required=True,
            choices=["yfinance", "ccxt", "twelvedata"],
            help="Data provider to use.",
        )
        parser.add_argument(
            "--symbol",
            required=True,
            help="Provider-native symbol format, e.g. BTC-USD, BTC/USDT, EUR/USD.",
        )
        parser.add_argument(
            "--timeframe",
            default="1h",
            help="Timeframe to ingest, e.g. 1m, 5m, 1h, 1day.",
        )
        parser.add_argument(
            "--limit",
            type=int,
            default=50,
            help="Row limit for providers that support it.",
        )
        parser.add_argument(
            "--period",
            default="7d",
            help="Used only for yfinance, e.g. 1d, 5d, 1mo, 3mo, 7d.",
        )
        parser.add_argument(
            "--outputsize",
            type=int,
            default=None,
            help="Used only for TwelveData. If omitted, --limit will be used.",
        )

    def handle(self, *args, **options):
        source = options["source"]
        symbol = options["symbol"]
        timeframe = options["timeframe"]
        limit = options["limit"]
        period = options["period"]
        outputsize = options["outputsize"] or limit

        self.stdout.write("Starting market data ingestion...")
        self.stdout.write(f"Source: {source}")
        self.stdout.write(f"Symbol: {symbol}")
        self.stdout.write(f"Timeframe: {timeframe}")

        try:
            if source == "yfinance":
                run = ingest_from_yfinance(
                    symbol=symbol,
                    timeframe=timeframe,
                    period=period,
                    limit=limit,
                )
            elif source == "ccxt":
                run = ingest_from_ccxt(
                    symbol=symbol,
                    timeframe=timeframe,
                    limit=limit,
                )
            elif source == "twelvedata":
                run = ingest_from_twelvedata(
                    symbol=symbol,
                    timeframe=timeframe,
                    outputsize=outputsize,
                )
            else:
                raise CommandError(f"Unsupported source: {source}")

        except Exception as exc:
            raise CommandError(f"Market ingestion failed: {exc}") from exc

        self.stdout.write(self.style.SUCCESS("Market ingestion completed successfully."))
        self.stdout.write(f"Run ID: {getattr(run, 'id', 'Unknown')}")
        self.stdout.write(f"Status: {getattr(run, 'status', 'Unknown')}")
        self.stdout.write(f"Rows inserted: {getattr(run, 'rows_inserted', 'Unknown')}")
        self.stdout.write(f"Rows updated: {getattr(run, 'rows_updated', 'Unknown')}")
        self.stdout.write(f"Rows skipped: {getattr(run, 'rows_skipped', 'Unknown')}")