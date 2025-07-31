from django.urls import path, include

from market.views.health_check import health_check

urlpatterns = [
    path("api/", include("market.urls")),
    path("health", health_check),
]
