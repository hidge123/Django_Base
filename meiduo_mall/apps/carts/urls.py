from django.urls import path
from apps.carts.views import CartView


urlpatterns = [
    path('carts/', CartView.as_view())
]