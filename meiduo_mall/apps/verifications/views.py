from random import randint
from django.shortcuts import render
from django.views import View
from libs.captcha.captcha import captcha
from django_redis import get_redis_connection
from django.http import HttpResponse, JsonResponse
from celery_tasks.sms.tasks import send_sms_code


# Create your views here.
class ImageCodeView(View):
    def get(self, request, uuid):
        # 生成图片验证码
        text, image = captcha.generate_captcha()
        
        # 通过redis将图片验证码保存
        redis_cli = get_redis_connection('code')
        redis_cli.setex(uuid, 100, text)

        return HttpResponse(image, content_type='image/jpeg')
    

class SmsCodeView(View):
    def get(self, request, mobile):
        # 获取参数
        uuid = request.GET.get('image_code_id')
        image_code = request.GET.get('image_code')
        # 验证参数
        if not all([image_code, uuid]):
            return JsonResponse({"code": 400, "errmsg": "参数不全"})
        # 检测发送标记
        redis_cli = get_redis_connection('code')
        send_flag = redis_cli.get('send_flag_%s' % mobile)
        if send_flag:
            return JsonResponse({"code": 400, "errmsg": "不要频繁发送短信验证码"})
        # 验证图片验证码
        redis_image_code = redis_cli.get(uuid)
        if redis_image_code is None:
            return JsonResponse({"code": 400, "errmsg": "图片验证码已过期"})
        elif redis_image_code.decode().lower() != image_code.lower():
            return JsonResponse({"code": 400, "errmsg": "图片验证码错误"})
        # 发送短信验证码并添加发送标记
        send_sms_code.delay(mobile)

        return JsonResponse({"code": "0", "errmsg": "ok"})
