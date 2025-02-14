"""
URL configuration for meiduo_mall project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.urls import include
from django.urls import register_converter
from utils.converters import MobileConverter, UsernameConverter, UUIDConverter, AreaConverter


register_converter(UsernameConverter, 'username')
register_converter(MobileConverter, 'mobile')
register_converter(UUIDConverter, 'uuid')
register_converter(AreaConverter, 'area')


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.users.urls')),
    path('', include('apps.verifications.urls')),
    path('', include('apps.oauth.urls')),
    path('', include('apps.areas.urls')),
    path('', include('apps.contents.urls')),
    path('', include('apps.goods.urls')),
    path('', include('apps.carts.urls')),
    path('', include('apps.orders.urls')),
    path('', include('apps.payment.urls'))
]
