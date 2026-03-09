from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("ops/", include("market_ingestion.operational_urls")),
    path("api/ops/", include("market_ingestion.api_urls")),
    path("", include("market_ingestion.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)