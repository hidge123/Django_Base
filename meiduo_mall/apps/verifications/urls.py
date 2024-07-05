from django.urls import path
from apps.verifications.views import ImageCodeView, SmsCodeView


urlpatterns = [
    path('image_codes/<uuid:uuid>/', ImageCodeView.as_view()),
    path('sms_codes/<mobile:mobile>/', SmsCodeView.as_view()),
]
