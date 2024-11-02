from django.urls import path
from apps.contents.views import IndexView


urlpatterns = [
    path('index/', IndexView.as_view()),
]