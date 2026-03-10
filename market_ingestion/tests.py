from decimal import Decimal
from io import StringIO
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.management import call_command

from django.urls import reverse
from django.utils import timezone
from django.test import TestCase, override_settings

TEST_STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}
from market_ingestion.models import (
    IngestionRun,
    MarketBar,
    MetricSnapshot,
    TradeJournalEntry,
)


class BaseDataMixin:
    def setUp(self):
        super().setUp()
        self.user_model = get_user_model()
        self.staff_user = self.user_model.objects.create_user(
            username="staffuser",
            email="staff@databridge.local",
            password="TestPass123!",
            is_staff=True,
        )
        self.regular_user = self.user_model.objects.create_user(
            username="regularuser",
            email="user@databridge.local",
            password="TestPass123!",
        )

        self.run = IngestionRun.objects.create(
            source="yfinance",
            symbol="BTC-USD",
            timeframe="1h",
            status="success",
            rows_inserted=10,
            rows_updated=5,
            rows_skipped=0,
            metadata={"provider": "yfinance"},
            finished_at=timezone.now(),
        )

        self.bar = MarketBar.objects.create(
            source="yfinance",
            symbol="BTC-USD",
            timeframe="1h",
            timestamp=timezone.now(),
            open=Decimal("62000.00000000"),
            high=Decimal("62500.00000000"),
            low=Decimal("61800.00000000"),
            close=Decimal("62400.00000000"),
            volume=Decimal("12.50000000"),
            ingestion_run=self.run,
            raw_payload={"example": True},
        )

        self.snapshot = MetricSnapshot.objects.create(
            symbol="BTC-USD",
            timeframe="1h",
            snapshot_time=timezone.now(),
            close_price=Decimal("62400.00000000"),
            return_1d=Decimal("0.01000000"),
            return_7d=Decimal("0.05000000"),
            volatility_14d=Decimal("0.02000000"),
            sma_fast=Decimal("62200.00000000"),
            sma_slow=Decimal("61800.00000000"),
            crossover_signal="bullish",
            source_run=self.run,
        )

        self.journal_entry = TradeJournalEntry.objects.create(
            symbol="BTC-USD",
            side="buy",
            opened_at=timezone.now(),
            closed_at=timezone.now(),
            open_price=Decimal("62000.00000000"),
            close_price=Decimal("62450.00000000"),
            size=Decimal("0.10000000"),
            pnl=Decimal("45.00000000"),
            source_file="trading-journal.csv",
            row_number=1,
            notes="test entry",
            raw_row={"row": 1},
            ingestion_run=self.run,
        )


@override_settings(STORAGES=TEST_STORAGES)
class HomeAndOpsTests(BaseDataMixin, TestCase):
    def test_home_page_loads(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "DataBridge")
        self.assertEqual(response.context["total_runs"], 1)
        self.assertEqual(response.context["total_bars"], 1)
        self.assertEqual(response.context["total_snapshots"], 1)
        self.assertEqual(response.context["total_journal_entries"], 1)

    def test_ops_dashboard_requires_staff_for_anonymous_user(self):
        response = self.client.get(reverse("ops:dashboard"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/admin/login/", response.url)

    def test_ops_dashboard_requires_staff_for_non_staff_user(self):
        self.client.login(username="regularuser", password="TestPass123!")
        response = self.client.get(reverse("ops:dashboard"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/admin/login/", response.url)

    def test_ops_dashboard_loads_for_staff(self):
        self.client.login(username="staffuser", password="TestPass123!")
        response = self.client.get(reverse("ops:dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Operations Dashboard")

    def test_ops_runs_page_loads_for_staff(self):
        self.client.login(username="staffuser", password="TestPass123!")
        response = self.client.get(reverse("ops:ingestion_runs"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Ingestion Runs")

    def test_ops_runs_filter_by_source(self):
        IngestionRun.objects.create(
            source="ccxt",
            symbol="BTC/USDT",
            timeframe="1h",
            status="success",
        )
        self.client.login(username="staffuser", password="TestPass123!")
        response = self.client.get(reverse("ops:ingestion_runs"), {"source": "yfinance"})
        self.assertEqual(response.status_code, 200)
        rows = response.context["rows"]
        self.assertTrue(rows)
        self.assertTrue(all(row["source"] == "yfinance" for row in rows))


@override_settings(STORAGES=TEST_STORAGES)
class APITests(BaseDataMixin, TestCase):
    def test_api_reference_loads(self):
        response = self.client.get(reverse("api_ops:reference"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "API Reference")
        self.assertContains(response, "Journal Entries")

    def test_runs_api_returns_expected_shape(self):
        response = self.client.get(reverse("api_ops:runs"))
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["endpoint"], "ingestion_runs")
        self.assertIn("meta", payload)
        self.assertIn("results", payload)
        self.assertEqual(payload["meta"]["total_results"], 1)
        self.assertEqual(payload["results"][0]["source"], "yfinance")

    def test_runs_api_filters_by_source(self):
        IngestionRun.objects.create(
            source="ccxt",
            symbol="BTC/USDT",
            timeframe="1h",
            status="success",
        )
        response = self.client.get(reverse("api_ops:runs"), {"source": "yfinance"})
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["meta"]["filters"]["source"], "yfinance")
        self.assertEqual(len(payload["results"]), 1)
        self.assertEqual(payload["results"][0]["source"], "yfinance")

    def test_run_detail_api_returns_expected_record(self):
        response = self.client.get(reverse("api_ops:run_detail", args=[self.run.id]))
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["endpoint"], "ingestion_run_detail")
        self.assertEqual(payload["result"]["id"], self.run.id)

    def test_snapshots_api_returns_expected_shape(self):
        response = self.client.get(reverse("api_ops:snapshots"))
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["endpoint"], "metric_snapshots")
        self.assertEqual(payload["meta"]["total_results"], 1)
        self.assertEqual(payload["results"][0]["symbol"], "BTC-USD")

    def test_bars_api_respects_page_size_cap(self):
        response = self.client.get(reverse("api_ops:bars"), {"page_size": 999})
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["meta"]["page_size"], 100)

    def test_bar_detail_api_returns_expected_record(self):
        response = self.client.get(reverse("api_ops:bar_detail", args=[self.bar.id]))
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["endpoint"], "market_bar_detail")
        self.assertEqual(payload["result"]["id"], self.bar.id)

    def test_journal_api_returns_expected_shape(self):
        response = self.client.get(reverse("api_ops:journal"))
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["endpoint"], "trade_journal_entries")
        self.assertEqual(payload["meta"]["total_results"], 1)
        self.assertEqual(payload["results"][0]["source_file"], "trading-journal.csv")

    def test_journal_api_filters_by_source_file(self):
        TradeJournalEntry.objects.create(
            symbol="ETH-USD",
            side="sell",
            source_file="other-journal.csv",
            row_number=2,
            raw_row={"row": 2},
        )
        response = self.client.get(
            reverse("api_ops:journal"),
            {"source_file": "trading-journal.csv"},
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["meta"]["filters"]["source_file"], "trading-journal.csv")
        self.assertEqual(len(payload["results"]), 1)
        self.assertEqual(payload["results"][0]["source_file"], "trading-journal.csv")

    def test_journal_detail_api_returns_expected_record(self):
        response = self.client.get(reverse("api_ops:journal_detail", args=[self.journal_entry.id]))
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["endpoint"], "trade_journal_entry_detail")
        self.assertEqual(payload["result"]["id"], self.journal_entry.id)


class CommandTests(BaseDataMixin, TestCase):
    @patch("market_ingestion.management.commands.ingest_market_data.ingest_from_yfinance")
    def test_ingest_market_data_command_calls_service_and_reports_success(self, mock_ingest):
        mock_run = IngestionRun(
            id=99,
            source="yfinance",
            symbol="BTC-USD",
            timeframe="1h",
            status="success",
            rows_inserted=1,
            rows_updated=49,
            rows_skipped=0,
        )
        mock_ingest.return_value = mock_run

        out = StringIO()
        call_command(
            "ingest_market_data",
            "--source", "yfinance",
            "--symbol", "BTC-USD",
            "--timeframe", "1h",
            "--limit", "50",
            "--period", "7d",
            stdout=out,
        )

        output = out.getvalue()
        self.assertIn("Market ingestion completed successfully.", output)
        self.assertIn("Run ID: 99", output)
        mock_ingest.assert_called_once_with(
            symbol="BTC-USD",
            timeframe="1h",
            period="7d",
            limit=50,
        )

    @patch("market_ingestion.management.commands.compute_metrics.compute_latest_metric_snapshot")
    def test_compute_metrics_command_links_to_run_and_reports_success(self, mock_compute):
        mock_compute.return_value = self.snapshot

        out = StringIO()
        call_command(
            "compute_metrics",
            "--symbol", "BTC-USD",
            "--timeframe", "1h",
            "--source", "yfinance",
            "--run-id", str(self.run.id),
            stdout=out,
        )

        output = out.getvalue()
        self.assertIn("Metric computation completed successfully.", output)
        self.assertIn(f"Snapshot ID: {self.snapshot.id}", output)
        mock_compute.assert_called_once_with(
            symbol="BTC-USD",
            timeframe="1h",
            source="yfinance",
            source_run=self.run,
        )

    @patch("market_ingestion.management.commands.import_trade_journal.import_trade_journal_csv")
    def test_import_trade_journal_command_calls_service_and_reports_success(self, mock_import):
        mock_run = IngestionRun(
            id=100,
            source="journal_csv",
            symbol="TRADE-JOURNAL",
            timeframe="",
            status="success",
            rows_inserted=422,
            rows_updated=0,
            rows_skipped=0,
        )
        mock_import.return_value = mock_run

        out = StringIO()
        call_command(
            "import_trade_journal",
            "market_ingestion/static/trading-journal.csv",
            stdout=out,
        )

        output = out.getvalue()
        self.assertIn("Trade journal import completed successfully.", output)
        self.assertIn("Run ID: 100", output)
        mock_import.assert_called_once_with("market_ingestion/static/trading-journal.csv")