from django.urls import path
from apps.oauth.views import QQAuthURLView


urlpatterns = [
    path('qq/authorization/', QQAuthURLView.as_view())
]