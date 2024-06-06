from django.urls import path
from apps.users.views import UserCountView


urlpatterns = [
    path('username/<username>/count/', UserCountView.as_view())
]