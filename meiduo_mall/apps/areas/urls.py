from django.urls import path
from apps.areas.views import AreaView


urlpatterns = [
    path('areas/', AreaView.as_view())
]