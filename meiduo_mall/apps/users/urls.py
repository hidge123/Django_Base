from django.urls import path
from apps.users.views import LoginView, LogoutView, MobileCountView, RegisterView, UserCountView, CenterView, EmailView, EmailVerifyView, AddressCreateView



urlpatterns = [
    path('usernames/<username:username>/count/', UserCountView.as_view()),
    path('mobiles/<mobile:mobile>/count/', MobileCountView.as_view()),
    path('register/', RegisterView.as_view()),
    path('login/', LoginView.as_view()),
    path('logout/', LogoutView.as_view()),
    path('info/', CenterView.as_view()),
    path('emails/', EmailView.as_view()),
    path('emails/verification/', EmailVerifyView.as_view()),
    path('addresses/create/', AddressCreateView.as_view())
]