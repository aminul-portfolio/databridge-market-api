from django.urls import path

from market_ingestion.operational_views import (
    ingestion_run_list,
    market_bar_list,
    metric_snapshot_list,
    ops_dashboard,
)

app_name = "ops"

urlpatterns = [
    path("", ops_dashboard, name="dashboard"),
    path("runs/", ingestion_run_list, name="ingestion_runs"),
    path("snapshots/", metric_snapshot_list, name="metric_snapshots"),
    path("bars/", market_bar_list, name="market_bars"),
]