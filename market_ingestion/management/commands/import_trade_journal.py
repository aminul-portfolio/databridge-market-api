from django.core.management.base import BaseCommand, CommandError

from market_ingestion.services.journal_import import import_trade_journal_csv


class Command(BaseCommand):
    help = "Import trade journal CSV into normalized trade journal models."

    def add_arguments(self, parser):
        parser.add_argument(
            "csv_path",
            nargs="?",
            default="market_ingestion/static/trading-journal.csv",
            help="Path to the trade journal CSV file.",
        )

    def handle(self, *args, **options):
        csv_path = options["csv_path"]

        self.stdout.write("Starting trade journal import...")
        self.stdout.write(f"CSV path: {csv_path}")

        try:
            run = import_trade_journal_csv(csv_path)
        except Exception as exc:
            raise CommandError(f"Trade journal import failed: {exc}") from exc

        self.stdout.write(self.style.SUCCESS("Trade journal import completed successfully."))
        self.stdout.write(f"Run ID: {getattr(run, 'id', 'Unknown')}")
        self.stdout.write(f"Status: {getattr(run, 'status', 'Unknown')}")
        self.stdout.write(f"Rows inserted: {getattr(run, 'rows_inserted', 'Unknown')}")
        self.stdout.write(f"Rows updated: {getattr(run, 'rows_updated', 'Unknown')}")
        self.stdout.write(f"Rows skipped: {getattr(run, 'rows_skipped', 'Unknown')}")