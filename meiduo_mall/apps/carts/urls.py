from django.urls import path
from apps.carts.views import CartView, CartSimpleView


urlpatterns = [
    path('carts/', CartView.as_view()),
    path('carts/simple/', CartSimpleView.as_view())
]