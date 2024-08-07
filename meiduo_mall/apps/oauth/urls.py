from django.urls import path
from apps.oauth.views import QQAuthURLView, OauthQQView


urlpatterns = [
    path('qq/authorization/', QQAuthURLView.as_view()),
    path('qq/oauth_callback/', OauthQQView.as_view()),
]