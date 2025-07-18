from django.urls import path

from market.views.api import KLineAPIView

urlpatterns = [
    path("kline/", KLineAPIView.as_view(), name="kline"),
]
