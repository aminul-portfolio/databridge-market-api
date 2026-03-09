from django.conf import settings


def app_shell(request):
    return {
        "APP_NAME": getattr(settings, "APP_NAME", "DataBridge"),
        "APP_ENV": getattr(settings, "APP_ENV", "dev"),
        "STREAMLIT_URL": getattr(settings, "STREAMLIT_URL", "http://127.0.0.1:8501"),
    }