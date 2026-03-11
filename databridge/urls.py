from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("market_ingestion.urls")),
    path("ops/", include(("market_ingestion.operational_urls", "ops"), namespace="ops")),
    path("api/ops/", include(("market_ingestion.api_urls", "api_ops"), namespace="api_ops")),
    path("demo/", include(("market_ingestion.demo_urls", "demo"), namespace="demo")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)