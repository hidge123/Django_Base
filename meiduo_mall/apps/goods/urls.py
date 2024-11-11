from django.urls import path
from apps.goods.views import ListView


urlpatterns = [
    path('list/<category_id>/skus/', ListView.as_view())
]
