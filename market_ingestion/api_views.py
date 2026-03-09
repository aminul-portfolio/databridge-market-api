from django.core.paginator import Paginator
from django.core.serializers.json import DjangoJSONEncoder
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render

from market_ingestion.models import IngestionRun, MarketBar, MetricSnapshot

def _get_int(value, default, minimum=1, maximum=200):
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return default
    return max(minimum, min(parsed, maximum))


def _build_meta(page_obj, page_size, filters):
    return {
        "page": page_obj.number,
        "page_size": page_size,
        "total_pages": page_obj.paginator.num_pages,
        "total_results": page_obj.paginator.count,
        "has_next": page_obj.has_next(),
        "has_previous": page_obj.has_previous(),
        "filters": filters,
    }

def api_reference_view(request):
    context = {
        "page_title": "API Reference",
        "runs_count": IngestionRun.objects.count(),
        "snapshots_count": MetricSnapshot.objects.count(),
        "bars_count": MarketBar.objects.count(),
    }
    return render(request, "market_ingestion/api_reference.html", context)

def ingestion_run_api(request):
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

    page = _get_int(request.GET.get("page"), default=1)
    page_size = _get_int(request.GET.get("page_size"), default=25, maximum=100)

    paginator = Paginator(queryset, page_size)
    page_obj = paginator.get_page(page)

    results = []
    for obj in page_obj.object_list:
        results.append(
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
                "error_message": obj.error_message,
                "metadata": obj.metadata,
            }
        )

    payload = {
        "endpoint": "ingestion_runs",
        "meta": _build_meta(
            page_obj,
            page_size,
            {
                "source": source,
                "symbol": symbol,
                "timeframe": timeframe,
                "status": status,
            },
        ),
        "results": results,
    }
    return JsonResponse(payload, encoder=DjangoJSONEncoder)


def metric_snapshot_api(request):
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

    page = _get_int(request.GET.get("page"), default=1)
    page_size = _get_int(request.GET.get("page_size"), default=25, maximum=100)

    paginator = Paginator(queryset, page_size)
    page_obj = paginator.get_page(page)

    results = []
    for obj in page_obj.object_list:
        results.append(
            {
                "id": obj.id,
                "symbol": obj.symbol,
                "timeframe": obj.timeframe,
                "snapshot_time": obj.snapshot_time,
                "close_price": obj.close_price,
                "return_1d": obj.return_1d,
                "return_7d": obj.return_7d,
                "volatility_14d": obj.volatility_14d,
                "sma_fast": obj.sma_fast,
                "sma_slow": obj.sma_slow,
                "crossover_signal": obj.crossover_signal,
                "source_run_id": obj.source_run_id,
                "source": obj.source_run.source if obj.source_run else None,
                "created_at": obj.created_at,
            }
        )

    payload = {
        "endpoint": "metric_snapshots",
        "meta": _build_meta(
            page_obj,
            page_size,
            {
                "source": source,
                "symbol": symbol,
                "timeframe": timeframe,
            },
        ),
        "results": results,
    }
    return JsonResponse(payload, encoder=DjangoJSONEncoder)


def market_bar_api(request):
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

    page = _get_int(request.GET.get("page"), default=1)
    page_size = _get_int(request.GET.get("page_size"), default=50, maximum=100)

    paginator = Paginator(queryset, page_size)
    page_obj = paginator.get_page(page)

    results = []
    for obj in page_obj.object_list:
        results.append(
            {
                "id": obj.id,
                "source": obj.source,
                "symbol": obj.symbol,
                "timeframe": obj.timeframe,
                "timestamp": obj.timestamp,
                "open": obj.open,
                "high": obj.high,
                "low": obj.low,
                "close": obj.close,
                "volume": obj.volume,
                "ingestion_run_id": obj.ingestion_run_id,
                "created_at": obj.created_at,
                "updated_at": obj.updated_at,
            }
        )

    payload = {
        "endpoint": "market_bars",
        "meta": _build_meta(
            page_obj,
            page_size,
            {
                "source": source,
                "symbol": symbol,
                "timeframe": timeframe,
            },
        ),
        "results": results,
    }
    return JsonResponse(payload, encoder=DjangoJSONEncoder)

def ingestion_run_detail_api(request, pk):
    obj = get_object_or_404(IngestionRun, pk=pk)

    payload = {
        "endpoint": "ingestion_run_detail",
        "result": {
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
            "error_message": obj.error_message,
            "metadata": obj.metadata,
        },
    }
    return JsonResponse(payload, encoder=DjangoJSONEncoder)


def metric_snapshot_detail_api(request, pk):
    obj = get_object_or_404(
        MetricSnapshot.objects.select_related("source_run"),
        pk=pk,
    )

    payload = {
        "endpoint": "metric_snapshot_detail",
        "result": {
            "id": obj.id,
            "symbol": obj.symbol,
            "timeframe": obj.timeframe,
            "snapshot_time": obj.snapshot_time,
            "close_price": obj.close_price,
            "return_1d": obj.return_1d,
            "return_7d": obj.return_7d,
            "volatility_14d": obj.volatility_14d,
            "sma_fast": obj.sma_fast,
            "sma_slow": obj.sma_slow,
            "crossover_signal": obj.crossover_signal,
            "source_run_id": obj.source_run_id,
            "source": obj.source_run.source if obj.source_run else None,
            "created_at": obj.created_at,
        },
    }
    return JsonResponse(payload, encoder=DjangoJSONEncoder)


def market_bar_detail_api(request, pk):
    obj = get_object_or_404(
        MarketBar.objects.select_related("ingestion_run"),
        pk=pk,
    )

    payload = {
        "endpoint": "market_bar_detail",
        "result": {
            "id": obj.id,
            "source": obj.source,
            "symbol": obj.symbol,
            "timeframe": obj.timeframe,
            "timestamp": obj.timestamp,
            "open": obj.open,
            "high": obj.high,
            "low": obj.low,
            "close": obj.close,
            "volume": obj.volume,
            "ingestion_run_id": obj.ingestion_run_id,
            "created_at": obj.created_at,
            "updated_at": obj.updated_at,
        },
    }
    return JsonResponse(payload, encoder=DjangoJSONEncoder)
