from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render

from market_ingestion.models import IngestionRun, MarketBar, MetricSnapshot


def _querystring_without_page(request):
    query = request.GET.copy()
    query.pop("page", None)
    return query.urlencode()


@login_required
def ingestion_run_list(request):
    queryset = IngestionRun.objects.all()

    source = request.GET.get("source", "").strip()
    symbol = request.GET.get("symbol", "").strip()
    timeframe = request.GET.get("timeframe", "").strip()
    status = request.GET.get("status", "").strip()

    if source:
        queryset = queryset.filter(source=source)
    if symbol:
        queryset = queryset.filter(symbol=symbol)
    if timeframe:
        queryset = queryset.filter(timeframe=timeframe)
    if status:
        queryset = queryset.filter(status=status)

    queryset = queryset.order_by("-started_at", "-id")

    paginator = Paginator(queryset, 25)
    page_obj = paginator.get_page(request.GET.get("page"))

    rows = []
    for obj in page_obj.object_list:
        rows.append(
            {
                "id": obj.id,
                "source": obj.source,
                "symbol": obj.symbol,
                "timeframe": obj.timeframe,
                "status": obj.status,
                "started_at": obj.started_at,
                "finished_at": obj.finished_at,
                "rows_inserted": obj.rows_inserted,
                "rows_updated": obj.rows_updated,
                "rows_skipped": obj.rows_skipped,
            }
        )

    context = {
        "page_title": "Ingestion Runs",
        "page_obj": page_obj,
        "rows": rows,
        "filter_choices": {
            "sources": list(
                IngestionRun.objects.order_by().values_list("source", flat=True).distinct()
            ),
            "symbols": list(
                IngestionRun.objects.order_by().values_list("symbol", flat=True).distinct()
            ),
            "timeframes": list(
                IngestionRun.objects.order_by().values_list("timeframe", flat=True).distinct()
            ),
            "statuses": list(
                IngestionRun.objects.order_by().values_list("status", flat=True).distinct()
            ),
        },
        "selected_filters": {
            "source": source,
            "symbol": symbol,
            "timeframe": timeframe,
            "status": status,
        },
        "querystring": _querystring_without_page(request),
        "current_section": "runs",
    }
    return render(request, "market_ingestion/ops/ingestion_run_list.html", context)


@login_required
def metric_snapshot_list(request):
    queryset = MetricSnapshot.objects.select_related("source_run").all()

    source = request.GET.get("source", "").strip()
    symbol = request.GET.get("symbol", "").strip()
    timeframe = request.GET.get("timeframe", "").strip()

    if source:
        queryset = queryset.filter(source_run__source=source)
    if symbol:
        queryset = queryset.filter(symbol=symbol)
    if timeframe:
        queryset = queryset.filter(timeframe=timeframe)

    queryset = queryset.order_by("-snapshot_time", "-id")

    paginator = Paginator(queryset, 25)
    page_obj = paginator.get_page(request.GET.get("page"))

    rows = []
    for obj in page_obj.object_list:
        rows.append(
            {
                "id": obj.id,
                "source": obj.source_run.source if obj.source_run else "—",
                "symbol": obj.symbol,
                "timeframe": obj.timeframe,
                "snapshot_time": obj.snapshot_time,
                "run_id": obj.source_run_id,
                "label": str(obj),
            }
        )

    context = {
        "page_title": "Metric Snapshots",
        "page_obj": page_obj,
        "rows": rows,
        "filter_choices": {
            "sources": list(
                IngestionRun.objects.order_by().values_list("source", flat=True).distinct()
            ),
            "symbols": list(
                MetricSnapshot.objects.order_by().values_list("symbol", flat=True).distinct()
            ),
            "timeframes": list(
                MetricSnapshot.objects.order_by().values_list("timeframe", flat=True).distinct()
            ),
            "statuses": [],
        },
        "selected_filters": {
            "source": source,
            "symbol": symbol,
            "timeframe": timeframe,
            "status": "",
        },
        "querystring": _querystring_without_page(request),
        "current_section": "snapshots",
    }
    return render(request, "market_ingestion/ops/metric_snapshot_list.html", context)


@login_required
def market_bar_list(request):
    queryset = MarketBar.objects.select_related("ingestion_run").all()

    source = request.GET.get("source", "").strip()
    symbol = request.GET.get("symbol", "").strip()
    timeframe = request.GET.get("timeframe", "").strip()

    if source:
        queryset = queryset.filter(source=source)
    if symbol:
        queryset = queryset.filter(symbol=symbol)
    if timeframe:
        queryset = queryset.filter(timeframe=timeframe)

    queryset = queryset.order_by("-timestamp", "-id")

    paginator = Paginator(queryset, 50)
    page_obj = paginator.get_page(request.GET.get("page"))

    rows = []
    for obj in page_obj.object_list:
        rows.append(
            {
                "id": obj.id,
                "source": obj.source,
                "symbol": obj.symbol,
                "timeframe": obj.timeframe,
                "bar_time": obj.timestamp,
                "open": obj.open,
                "high": obj.high,
                "low": obj.low,
                "close": obj.close,
                "volume": obj.volume,
                "run_id": obj.ingestion_run_id,
            }
        )

    context = {
        "page_title": "Market Bars",
        "page_obj": page_obj,
        "rows": rows,
        "filter_choices": {
            "sources": list(
                MarketBar.objects.order_by().values_list("source", flat=True).distinct()
            ),
            "symbols": list(
                MarketBar.objects.order_by().values_list("symbol", flat=True).distinct()
            ),
            "timeframes": list(
                MarketBar.objects.order_by().values_list("timeframe", flat=True).distinct()
            ),
            "statuses": [],
        },
        "selected_filters": {
            "source": source,
            "symbol": symbol,
            "timeframe": timeframe,
            "status": "",
        },
        "querystring": _querystring_without_page(request),
        "current_section": "bars",
    }
    return render(request, "market_ingestion/ops/market_bar_list.html", context)