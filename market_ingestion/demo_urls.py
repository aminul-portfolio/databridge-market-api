from django.urls import path
from . import views

app_name = "demo"

urlpatterns = [
    # BTC yfinance
    path("btc-yfinance/", views.btc_yfinance, name="btc_yfinance"),
    path("btc-yfinance-page/", views.btc_yfinance_page, name="btc_yfinance_page"),
    path("btc-yfinance-info/", views.btc_yfinance_info, name="btc_yfinance_info"),
    path("btc-yfinance-compare/", views.btc_yfinance_compare, name="btc_yfinance_compare"),
    path("btc-yfinance-plot/", views.btc_yfinance_plot, name="btc_yfinance_plot"),

    # BTC ccxt
    path("btc-ccxt/", views.btc_ccxt, name="btc_ccxt"),
    path("btc-ccxt-page/", views.btc_ccxt_page, name="btc_ccxt_page"),

    # EUR/USD TwelveData
    path("eurusd-twelvedata-page/", views.eurusd_twelvedata_page, name="eurusd_twelvedata_page"),
    path("eurusd-twelvedata-json/", views.eurusd_twelvedata_json, name="eurusd_twelvedata_json"),
]