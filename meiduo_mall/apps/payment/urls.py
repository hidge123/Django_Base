from django.urls import path
from apps.payment.views import PayUrlVIew
from django.urls import re_path


urlpatterns = [
    re_path(r'^payment/(?P<order_id>\d+)/$', PayUrlVIew.as_view())
]