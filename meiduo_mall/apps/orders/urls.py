from django.urls import path
from apps.orders.views import OrderSettlementView


urlpatterns = [
    path('orders/settlement/', OrderSettlementView.as_view())
]
