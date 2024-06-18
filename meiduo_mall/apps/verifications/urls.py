from django.urls import path
from apps.verifications.views import ImageCodeView


urlpatterns = [
    path('image_codes/<uuid>/', ImageCodeView.as_view())
]