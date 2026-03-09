# DataBridge Market API

A production-minded Django market data ingestion and analytics platform that ingests multi-source financial data, stores normalized historical records, tracks ingestion runs, computes metric snapshots, exposes a read-only API layer, and provides a SaaS-style operational UI.

## Why this project matters

DataBridge Market API was upgraded from a live-data demo into a more structured data platform designed to demonstrate capability for:

- Analytics Engineer
- Data Engineer [Junior / Integration]
- FinTech analytics
- Reporting / Analytics Engineer
- Python / Django data-product roles

This project is intentionally built around operational credibility rather than only page-level demos:

- provider clients
- service-layer orchestration
- normalized persistence
- ETL-style management commands
- operational inspection UI
- read-only API endpoints
- human-readable API reference page

---

## What it does

### Multi-source ingestion
The platform ingests market data from:

- yfinance
- ccxt
- TwelveData

### Normalized storage
It stores market and analytics data in structured models instead of relying only on raw API responses:

- `IngestionRun`
- `MarketBar`
- `MetricSnapshot`
- `TradeJournalEntry`

### Repeatable ETL workflows
It supports reusable terminal-driven workflows for:

- ingesting market data
- importing trade journal CSV files
- computing metric snapshots

### Operational UI
It includes SaaS-style internal operational pages for:

- ingestion runs
- metric snapshots
- market bars

### Read-only API layer
It exposes JSON endpoints for:

- runs
- snapshots
- bars
- detail endpoints by id

### API reference
It includes a human-readable API reference page documenting:

- available endpoints
- supported query params
- example URLs
- example response shapes

---

## Architecture flow

```text
provider client -> service layer -> normalized database models -> ETL commands -> API layer -> metrics outputs -> deployment

databridge-market-api/
├─ README.md
├─ manage.py
├─ requirements.txt
├─ .env.example
├─ databridge/
│  ├─ urls.py
│  └─ settings/
│     ├─ base.py
│     ├─ dev.py
│     └─ prod.py
├─ market_ingestion/
│  ├─ clients/
│  │  ├─ yfinance_client.py
│  │  ├─ ccxt_client.py
│  │  └─ twelvedata_client.py
│  ├─ services/
│  │  ├─ ingestion.py
│  │  ├─ journal_import.py
│  │  └─ metrics.py
│  ├─ management/
│  │  └─ commands/
│  │     ├─ ingest_market_data.py
│  │     ├─ import_trade_journal.py
│  │     └─ compute_metrics.py
│  ├─ templates/
│  │  ├─ base.html
│  │  ├─ home.html
│  │  └─ market_ingestion/
│  │     ├─ api_reference.html
│  │     ├─ layouts/
│  │     │  └─ app_shell.html
│  │     ├─ ops/
│  │     │  ├─ ingestion_run_list.html
│  │     │  ├─ metric_snapshot_list.html
│  │     │  └─ market_bar_list.html
│  │     └─ partials/
│  │        ├─ _sidebar.html
│  │        └─ _topbar.html
│  ├─ static/
│  │  └─ market_ingestion/
│  │     └─ css/
│  │        ├─ app.css
│  │        └─ tokens.css
│  ├─ api_views.py
│  ├─ api_urls.py
│  ├─ operational_views.py
│  ├─ operational_urls.py
│  ├─ models.py
│  ├─ admin.py
│  ├─ urls.py
│  └─ views.py
├─ streamlit_app.py
└─ docs/
   ├─ STATUS.md
   ├─ PROOF_INDEX.md
   └─ screenshots/