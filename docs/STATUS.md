# DataBridge Market API — STATUS

## What this project is

DataBridge Market API is a production-minded Django data product for multi-source market data ingestion, normalized storage, and analytics delivery. It is designed to demonstrate the upstream engineering work that makes analytics possible — not just a dashboard layer, but the full pipeline behind it.

**Core capabilities:**
- Multi-source financial data ingestion (yfinance, ccxt, TwelveData)
- Normalized historical storage with a clean relational model
- Ingestion run tracking and ETL observability via `IngestionRun`
- Metric snapshot generation (returns, volatility, SMA, crossover signals) via `MetricSnapshot`
- ETL-style Django management commands (`ingest_market_data`, `import_trade_journal`, `compute_metrics`)
- Operational monitoring UI
- Read-only JSON API with filtering and human-readable reference docs
- SaaS-style public portfolio presentation

**Built for roles including:**
- Analytics Engineer
- Data Engineer (Junior / Integration)
- FinTech Analytics
- BI / Reporting Engineer
- Python / Django data-product roles

---

## Architecture flow

```
Provider Clients    →    Service Layer       →    Normalized Models    →    ETL Commands           →    API + Ops UI    →    Analytics Output
yfinance                 ingestion.py             IngestionRun               ingest_market_data          /api/ops/            Streamlit
ccxt                     journal_import.py        MarketBar                  import_trade_journal        /ops/
TwelveData               metrics.py               MetricSnapshot             compute_metrics             /portfolio/
                                                  TradeJournalEntry                                      /
```

---

## Current state

Packaged as a portfolio-ready artifact with core review surfaces in place.

| Surface | Status |
|---------|--------|
| Ingestion commands (`ingest_market_data`, `import_trade_journal`) | ✅ Operational across all three providers |
| Metric computation (`compute_metrics` → `MetricSnapshot`) | ✅ Verified |
| `IngestionRun` observability surfaced on dashboard | ✅ Verified |
| Read-only API endpoints with filtering | ✅ Live |
| Operations UI (`/ops/runs/`, `/ops/snapshots/`, `/ops/bars/`) | ✅ Functional |
| Streamlit analytics surface | ✅ Connected |
| Public landing page (`/portfolio/`) | ✅ Recruiter-ready |
| Executive dashboard (`/`) | ✅ KPI summary live |
| Proof artifacts under `docs/` | ✅ Screenshots and index in place |

---

## Verified proof items

| Item | Notes |
|------|-------|
| `IngestionRun` records created | Confirmed via `/ops/runs/` |
| `MarketBar` OHLCV records stored | Confirmed via `/api/ops/bars/` |
| `MetricSnapshot` outputs computed | Confirmed via `/api/ops/snapshots/` |
| `TradeJournalEntry` import working | Confirmed via `/api/ops/journal/` |
| ETL run log visible on dashboard | Confirmed via `/ops/` |
| API reference documentation | Available at `/api/ops/reference/` |
| Full dashboard screenshot | `docs/screenshots/01.0_home_dashboard_full.png` |

---

## Proof artifacts

| Artifact | Location |
|----------|----------|
| All screenshots | `docs/screenshots/` |
| Proof index | `docs/PROOF_INDEX.md` |
| This status file | `docs/STATUS.md` |

---

## What still warrants a final check before submission

- Confirm all screenshot filenames in `docs/screenshots/` match paths referenced in `README.md`
- Verify `TWELVEDATA_API_KEY` is not committed anywhere in the repo
- Confirm `.env.example` lists all required keys
- Run `python manage.py check` and `python manage.py test` to confirm clean state
