from django.urls import path

from market.serializers.aggregated_kline import AggregatedKLineSerializer
from market.views.aggregated_kline import AggregatedKLineListView
from market.views.kline import KLineView

urlpatterns = [
    path("kline/", KLineView.as_view(), name="kline"),
    path("aggregatedkline/", AggregatedKLineListView.as_view(), name="aggregatedkline-list"),
]
