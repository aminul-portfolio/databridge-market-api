from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("portfolio/", views.public_landing, name="public_landing"),
    path("portfolio", views.public_landing),
]