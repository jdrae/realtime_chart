from django.urls import path

from market.views.aggregated_kline import AggregatedKLineListView, AggregatedKLineDetailView
from market.views.kline import KLineView

urlpatterns = [
    path("kline/", KLineView.as_view(), name="kline"),
    path("aggregatedkline/detail/", AggregatedKLineDetailView.as_view(), name="aggregatedkline-detail"),
    path("aggregatedkline/list/", AggregatedKLineListView.as_view(), name="aggregatedkline-list"),
]
