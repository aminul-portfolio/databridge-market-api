import os

from django.core.exceptions import ImproperlyConfigured

from .base import *


DEBUG = False

# Require an explicit production secret key
raw_secret_key = os.getenv("SECRET_KEY", "").strip()
if not raw_secret_key or raw_secret_key == "change-me":
    raise ImproperlyConfigured("SECRET_KEY must be set to a real value in production.")

SECRET_KEY = raw_secret_key

# Require explicit production hosts instead of inheriting localhost defaults
raw_allowed_hosts = os.getenv("ALLOWED_HOSTS", "").strip()
if not raw_allowed_hosts:
    raise ImproperlyConfigured("ALLOWED_HOSTS must be set in production.")

ALLOWED_HOSTS = [host.strip() for host in raw_allowed_hosts.split(",") if host.strip()]

# CSRF trusted origins are strongly recommended for deployed environments
raw_csrf_trusted_origins = os.getenv("CSRF_TRUSTED_ORIGINS", "").strip()
CSRF_TRUSTED_ORIGINS = [
    origin.strip()
    for origin in raw_csrf_trusted_origins.split(",")
    if origin.strip()
]

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = True

SECURE_HSTS_SECONDS = 60 * 60 * 24 * 30
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = "DENY"