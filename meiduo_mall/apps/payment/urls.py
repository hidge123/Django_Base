from django.urls import path
from apps.payment.views import PayUrlVIew, PayStatusView
from django.urls import re_path


urlpatterns = [
    path('payment/status/', PayStatusView.as_view()),
    re_path(r'^payment/(?P<order_id>\d+)/$', PayUrlVIew.as_view()),
 
]