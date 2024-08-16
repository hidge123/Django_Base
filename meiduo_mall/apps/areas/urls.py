from django.urls import path
from apps.areas.views import AreaView, SubAreaView


urlpatterns = [
    path('areas/', AreaView.as_view()),
    path('areas/<area:id>/', SubAreaView.as_view())
]
