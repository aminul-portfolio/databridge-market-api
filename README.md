<div align="center">
<img src="https://capsule-render.vercel.app/api?type=rect&color=0d1117,1c2128,0d1117&height=3" width="100%"/>
</div>

<br/>

<div align="center">
<img src="https://capsule-render.vercel.app/api?type=soft&color=0d1117&height=200&text=DataBridge%20Market%20API&fontSize=40&fontColor=e8d5a3&fontAlignY=44&desc=Multi-source%20Market%20Data%20Ingestion%20%C2%B7%20ETL%20%C2%B7%20Normalized%20Storage%20%C2%B7%20Read-only%20API&descSize=13&descAlignY=66&descColor=6b7280&animation=fadeIn" width="100%"/>
</div>

<br/>

<div align="center">

![Python](https://img.shields.io/badge/Python-0d1117?style=for-the-badge&logo=python&logoColor=e8d5a3)&nbsp;
![Django](https://img.shields.io/badge/Django-0d1117?style=for-the-badge&logo=django&logoColor=e8d5a3)&nbsp;
![Streamlit](https://img.shields.io/badge/Streamlit-0d1117?style=for-the-badge&logo=streamlit&logoColor=e8d5a3)&nbsp;
![SQLite](https://img.shields.io/badge/SQLite-0d1117?style=for-the-badge&logo=sqlite&logoColor=e8d5a3)

</div>

<br/>

<div align="center">

![yfinance](https://img.shields.io/badge/yfinance-1c2128?style=flat-square)&nbsp;
![ccxt](https://img.shields.io/badge/ccxt-1c2128?style=flat-square)&nbsp;
![TwelveData](https://img.shields.io/badge/TwelveData-1c2128?style=flat-square)&nbsp;
![ETL](https://img.shields.io/badge/ETL_Workflows-1c2128?style=flat-square)&nbsp;
![REST API](https://img.shields.io/badge/Read--only_API-1c2128?style=flat-square)&nbsp;
![Portfolio](https://img.shields.io/badge/Portfolio_Project-e8d5a3?style=flat-square&color=1c2128&labelColor=0d1117)

</div>

<br/><br/>

<!------------------------------------------------------------------>
<img src="https://capsule-render.vercel.app/api?type=rect&color=0d1117&height=68&text=%2001%20%2F%20What%20This%20Is&fontSize=20&fontColor=e8d5a3&fontAlign=12&fontAlignY=52&desc=Django%20data%20product%20for%20multi-source%20market%20data%20ingestion%20and%20analytics%20delivery&descSize=12&descColor=6b7280&descAlign=50&descAlignY=78" width="100%"/>
<!------------------------------------------------------------------>

<br/>

A Django data product for **multi-source market data ingestion**, normalized storage, ETL [Extract, Transform, Load] workflows, operational visibility, and read-only API delivery — built to demonstrate Analytics Engineer, Data Engineer, FinTech, and BI [Business Intelligence] / reporting-oriented capability.

```
Source ingestion  →  Normalized storage  →  Metric computation  →  Operational visibility  →  API delivery  →  Analytics consumption
```

**Includes:** multi-source ingestion commands, normalized models, metric snapshots, operations UI, read-only JSON API, Streamlit output, and proof artifacts under `docs/`.

<br/>

<!------------------------------------------------------------------>
<img src="https://capsule-render.vercel.app/api?type=rect&color=0d1117&height=68&text=%2002%20%2F%20For%20Hiring%20Managers&fontSize=20&fontColor=e8d5a3&fontAlign=13&fontAlignY=52&desc=The%20upstream%20engineering%20side%20of%20analytics%20work%20%E2%80%94%20full%20pipeline%2C%20not%20just%20dashboards&descSize=12&descColor=6b7280&descAlign=50&descAlignY=78" width="100%"/>
<!------------------------------------------------------------------>

<br/>

This project demonstrates the **upstream engineering side** of analytics work — not just charts and dashboards, but the full pipeline that makes them possible.

<table width="100%">
<tr>
<td width="50%" valign="top">

**Analytics Engineer / BI Engineer**

| Capability | Detail |
|:---|:---|
| Data model | Normalized relational model for downstream reporting |
| Metrics | Reusable snapshot computation — returns, volatility, SMA, crossover signals |
| API | Read-only endpoints with filtering and human-readable reference docs |
| Output | Analyst-facing Streamlit surface |

</td>
<td width="50%" valign="top">

**Data Engineer / Junior Integration Engineer**

| Capability | Detail |
|:---|:---|
| Integrations | Three live providers — yfinance, ccxt, TwelveData |
| ETL | Repeatable workflows via Django management commands |
| Observability | Status, timestamps, row counts, and execution context logged per run |

</td>
</tr>
</table>

**The interview story in one sentence:**

> *"External market data from multiple providers flows through ingestion commands into a normalized store, metric snapshots are computed on demand, and everything is queryable via a read-only API with an ops monitoring UI."*

<br/>

<!------------------------------------------------------------------>
<img src="https://capsule-render.vercel.app/api?type=rect&color=0d1117&height=68&text=%2003%20%2F%20Architecture&fontSize=20&fontColor=e8d5a3&fontAlign=11&fontAlignY=52&desc=Provider%20clients%20%E2%86%92%20service%20layer%20%E2%86%92%20normalized%20models%20%E2%86%92%20delivery%20layer&descSize=12&descColor=6b7280&descAlign=50&descAlignY=78" width="100%"/>
<!------------------------------------------------------------------>

<br/>

```
Provider Clients        Service Layer             Normalized Models
─────────────────       ──────────────────────    ──────────────────────
yfinance                ingestion.py              IngestionRun
ccxt              ──▶   journal_import.py   ──▶   MarketBar
TwelveData              metrics.py                MetricSnapshot
                                                  TradeJournalEntry
                                                         ↓
                        ETL Commands              Delivery Layer
                        ──────────────────────    ──────────────────────
                        ingest_market_data         /api/ops/   JSON endpoints
                        import_trade_journal  ──▶  /ops/       monitoring UI
                        compute_metrics            /portfolio/ public landing
                                                   /           exec dashboard
                                                   streamlit   analytics output
```

<br/>

<!------------------------------------------------------------------>
<img src="https://capsule-render.vercel.app/api?type=rect&color=0d1117&height=68&text=%2004%20%2F%20Core%20Models&fontSize=20&fontColor=e8d5a3&fontAlign=11&fontAlignY=52&desc=IngestionRun%20%C2%B7%20MarketBar%20%C2%B7%20MetricSnapshot%20%C2%B7%20TradeJournalEntry&descSize=12&descColor=6b7280&descAlign=50&descAlignY=78" width="100%"/>
<!------------------------------------------------------------------>

<br/>

| Model | Purpose |
|:---|:---|
| **`IngestionRun`** | ETL execution metadata — source, symbol, timeframe, status, row counts, timestamps, execution context |
| **`MarketBar`** | Normalized OHLCV records linked to an ingestion run for downstream analytics and operational inspection |
| **`MetricSnapshot`** | Computed analytics outputs — return windows, volatility, SMA fast/slow values, and crossover signals |
| **`TradeJournalEntry`** | Imported journal data for portfolio analytics context, inspection views, and comparison workflows |

<br/>

<!------------------------------------------------------------------>
<img src="https://capsule-render.vercel.app/api?type=rect&color=0d1117&height=68&text=%2005%20%2F%20Product%20Surfaces&fontSize=20&fontColor=e8d5a3&fontAlign=12&fontAlignY=52&desc=Six%20distinct%20surfaces%20%C2%B7%20operational%20%C2%B7%20API%20%C2%B7%20analyst-facing%20%C2%B7%20recruiter-facing&descSize=12&descColor=6b7280&descAlign=50&descAlignY=78" width="100%"/>
<!------------------------------------------------------------------>

<br/>

| Route | Surface | Purpose |
|:---|:---|:---|
| `/` | Executive dashboard | KPI summary, latest run state, platform navigation |
| `/portfolio/` | Public landing page | Recruiter-facing project overview |
| `/ops/` | Operations UI | ETL run history, snapshots, bars, platform state |
| `/api/ops/` | Read-only API | JSON endpoints with filtering and detail routes |
| `/demo/` | Source previews | Controlled provider proof routes |
| `streamlit_app.py` | Analytics surface | Analyst-facing chart and market-view output |

<br/>

<!------------------------------------------------------------------>
<img src="https://capsule-render.vercel.app/api?type=rect&color=0d1117&height=68&text=%2006%20%2F%20API%20Endpoints&fontSize=20&fontColor=e8d5a3&fontAlign=11&fontAlignY=52&desc=All%20endpoints%20are%20read-only%20and%20support%20query%20parameter%20filtering&descSize=12&descColor=6b7280&descAlign=50&descAlignY=78" width="100%"/>
<!------------------------------------------------------------------>

<br/>

| Method | Endpoint | Description |
|:---|:---|:---|
| GET | `/api/ops/reference/` | Human-readable API documentation |
| GET | `/api/ops/runs/` | Ingestion run list — filter by source, status, symbol |
| GET | `/api/ops/runs/<id>/` | Ingestion run detail |
| GET | `/api/ops/snapshots/` | Metric snapshot list — filter by symbol, timeframe |
| GET | `/api/ops/bars/` | Market bar OHLCV records — filter by symbol, timeframe |
| GET | `/api/ops/journal/` | Trade journal entries — filter by source_file |

<br/>

<!------------------------------------------------------------------>
<img src="https://capsule-render.vercel.app/api?type=rect&color=0d1117&height=68&text=%2007%20%2F%20How%20to%20Review&fontSize=20&fontColor=e8d5a3&fontAlign=12&fontAlignY=52&desc=Six%20review%20paths%20for%20hiring%20managers%20and%20technical%20reviewers&descSize=12&descColor=6b7280&descAlign=50&descAlignY=78" width="100%"/>
<!------------------------------------------------------------------>

<br/>

**1. Public landing page** — `/portfolio/`
Recruiter-facing overview of capabilities, architecture, data models, API layer, and stack.

**2. Executive dashboard** — `/`
KPI-style operational summary, latest run state, and platform navigation.

**3. ETL execution history** — `/ops/runs/`
Ingestion run history with status, timestamps, and row-level execution tracking.

**4. API layer** — `/api/ops/reference/`
Human-readable documentation for all read-only JSON endpoints.

**5. Analyst-facing output** — `streamlit_app.py`
```bash
python -m streamlit run streamlit_app.py
```

**6. ETL commands directly**
```bash
python manage.py ingest_market_data --source yfinance --symbol BTC-USD --timeframe 1h --limit 50 --period 7d
python manage.py import_trade_journal market_ingestion/static/trading-journal.csv
python manage.py compute_metrics --symbol BTC-USD --timeframe 1h --source yfinance --run-id <RUN_ID>
```

**7. Proof artifacts** — `docs/STATUS.md`, `docs/PROOF_INDEX.md`, `docs/screenshots/`

<br/>

<!------------------------------------------------------------------>
<img src="https://capsule-render.vercel.app/api?type=rect&color=0d1117&height=68&text=%2008%20%2F%20ETL%20Commands&fontSize=20&fontColor=e8d5a3&fontAlign=11&fontAlignY=52&desc=Repeatable%20Django%20management%20commands%20for%20ingestion%20and%20metric%20computation&descSize=12&descColor=6b7280&descAlign=50&descAlignY=78" width="100%"/>
<!------------------------------------------------------------------>

<br/>

```bash
# Ingest market data
python manage.py ingest_market_data \
  --source yfinance \
  --symbol BTC-USD \
  --timeframe 1h \
  --limit 50 \
  --period 7d

# Import trade journal
python manage.py import_trade_journal market_ingestion/static/trading-journal.csv

# Compute metric snapshot
python manage.py compute_metrics \
  --symbol BTC-USD \
  --timeframe 1h \
  --source yfinance \
  --run-id <RUN_ID>
```

<br/>

<!------------------------------------------------------------------>
<img src="https://capsule-render.vercel.app/api?type=rect&color=0d1117&height=68&text=%2009%20%2F%20Local%20Setup&fontSize=20&fontColor=e8d5a3&fontAlign=11&fontAlignY=52&desc=Install%20%C2%B7%20configure%20%C2%B7%20migrate%20%C2%B7%20run&descSize=12&descColor=6b7280&descAlign=50&descAlignY=78" width="100%"/>
<!------------------------------------------------------------------>

<br/>

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure environment
# Copy .env.example to .env and fill in:
#   DJANGO_SETTINGS_MODULE
#   TWELVEDATA_API_KEY
#   STREAMLIT_URL
#   CCXT_EXCHANGE

# 3. Run Django
python manage.py migrate
python manage.py runserver

# 4. Run Streamlit (optional)
python -m streamlit run streamlit_app.py

# 5. Verify
python manage.py check
python manage.py test
```

> TwelveData preview pages require a valid `TWELVEDATA_API_KEY` in `.env`. Real secrets must never be committed.

<br/>

<!------------------------------------------------------------------>
<img src="https://capsule-render.vercel.app/api?type=rect&color=0d1117&height=68&text=%2010%20%2F%20Tech%20Stack%20%26%20Structure&fontSize=20&fontColor=e8d5a3&fontAlign=13&fontAlignY=52&desc=Python%20%C2%B7%20Django%20%C2%B7%20yfinance%20%C2%B7%20ccxt%20%C2%B7%20TwelveData%20%C2%B7%20Streamlit%20%C2%B7%20SQLite&descSize=12&descColor=6b7280&descAlign=50&descAlignY=78" width="100%"/>
<!------------------------------------------------------------------>

<br/>

<table width="100%">
<tr>
<td width="40%" valign="top">

**Tech Stack**

| Layer | Technology |
|:---|:---|
| Backend | Python / Django |
| Market data | yfinance |
| Crypto data | ccxt |
| Financial API | TwelveData |
| Analytics UI | Streamlit |
| Database | SQLite (dev) / PostgreSQL (production target) |
| Testing | Django TestCase |

</td>
<td width="60%" valign="top">

**Project Structure**

```
databridge-market-api/
├── manage.py
├── requirements.txt
├── .env.example
├── streamlit_app.py
├── databridge/
│   ├── urls.py
│   └── settings/
│       ├── base.py
│       ├── dev.py
│       └── prod.py
├── market_ingestion/
│   ├── clients/
│   │   ├── yfinance_client.py
│   │   ├── ccxt_client.py
│   │   └── twelvedata_client.py
│   ├── services/
│   │   ├── ingestion.py
│   │   ├── journal_import.py
│   │   └── metrics.py
│   ├── management/commands/
│   └── models.py
└── docs/
    ├── STATUS.md
    ├── PROOF_INDEX.md
    └── screenshots/
```

</td>
</tr>
</table>

<br/>

<!------------------------------------------------------------------>
<img src="https://capsule-render.vercel.app/api?type=rect&color=0d1117&height=68&text=%2011%20%2F%20Screenshots&fontSize=20&fontColor=e8d5a3&fontAlign=11&fontAlignY=52&desc=Public%20landing%20%C2%B7%20Executive%20dashboard%20%C2%B7%20Ingestion%20runs%20%C2%B7%20API%20reference%20%C2%B7%20Streamlit&descSize=12&descColor=6b7280&descAlign=50&descAlignY=78" width="100%"/>
<!------------------------------------------------------------------>

<br/>

### Public Landing Page
![Public Landing Hero](docs/screenshots/00.1_public_landing_hero.png)

### Core Product Surfaces

| Executive Dashboard | Ingestion Runs |
|:---|:---|
| ![Executive Dashboard](docs/screenshots/01.1_home_dashboard.png) | ![Ingestion Runs](docs/screenshots/03_ingestion_runs.png) |

| API Reference | Streamlit Dashboard |
|:---|:---|
| ![API Reference](docs/screenshots/06.1_api_reference.png) | ![Streamlit Dashboard](docs/screenshots/11.2_streamlit_dashboard.png) |

[Full executive dashboard screenshot](docs/screenshots/01.0_home_dashboard_full.png)

<br/><br/>

---

<div align="center">

[![Portfolio Site](https://img.shields.io/badge/◈_PORTFOLIO_SITE-e8d5a3?style=for-the-badge&logoColor=0d1117)](https://aminul-portfolio.github.io)&nbsp;&nbsp;
[![GitHub Profile](https://img.shields.io/badge/GITHUB_PROFILE-0d1117?style=for-the-badge&logo=github&logoColor=e8d5a3)](https://github.com/aminul-portfolio)&nbsp;&nbsp;
[![LinkedIn](https://img.shields.io/badge/LINKEDIN-0a66c2?style=for-the-badge&logo=linkedin&logoColor=ffffff)](https://www.linkedin.com/in/aminul-islam-a71a871a2)

</div>

<br/>

---

<div align="center">
<sub>Portfolio project · seeded demo data · SQLite dev database · no production deployment · no live customers</sub>
</div>

<br/>

<div align="center">
<img src="https://capsule-render.vercel.app/api?type=rect&color=0d1117,1c2128,0d1117&height=3" width="100%"/>
</div>
