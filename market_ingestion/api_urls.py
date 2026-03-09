from django.urls import path

from market_ingestion.api_views import (
    api_reference_view,
    ingestion_run_api,
    ingestion_run_detail_api,
    market_bar_api,
    market_bar_detail_api,
    metric_snapshot_api,
    metric_snapshot_detail_api,
)

app_name = "api_ops"

urlpatterns = [
    path("", api_reference_view, name="reference"),
    path("runs/", ingestion_run_api, name="runs"),
    path("runs/<int:pk>/", ingestion_run_detail_api, name="run_detail"),
    path("snapshots/", metric_snapshot_api, name="snapshots"),
    path("snapshots/<int:pk>/", metric_snapshot_detail_api, name="snapshot_detail"),
    path("bars/", market_bar_api, name="bars"),
    path("bars/<int:pk>/", market_bar_detail_api, name="bar_detail"),
]