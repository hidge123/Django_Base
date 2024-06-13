from django.urls import path
from apps.users.views import MobileCountView, RegisterView, UserCountView



urlpatterns = [
    path('usernames/<username:username>/count/', UserCountView.as_view()),
    path('mobiles/<mobile:mobile>/count/', MobileCountView.as_view()),
    path('register/', RegisterView.as_view())
]