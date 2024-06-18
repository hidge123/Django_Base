from django.shortcuts import render
from django.views import View
from libs.captcha.captcha import captcha
from django_redis import get_redis_connection
from django.http import HttpResponse

# Create your views here.
class ImageCodeView(View):
    def get(self, request, uuid):
        # 生成图片验证码
        text, image = captcha.generate_captcha()
        
        # 通过redis将图片验证码保存
        redis_cli = get_redis_connection('code')
        redis_cli.setex(uuid, 100, text)

        return HttpResponse(image, content_type='image/jpeg')
    