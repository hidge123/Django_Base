from json import loads
import re
from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
from apps.users.models import User
from django.contrib.auth import login
from django_redis import get_redis_connection


# Create your views here.
class UserCountView(View):
    def get(self, request, username):
        count = User.objects.filter(username=username).count()

        return JsonResponse({"code": 0, "count": count, "errmsg": "ok"})


class MobileCountView(View):
    def get(self, request, mobile):
        count = User.objects.filter(mobile=mobile).count()

        return JsonResponse({"code": 0, "count": count, "errmsg": "ok"})


class RegisterView(View):
    def post(self, request):
        # 接受请求
        body_str = request.body.decode()
        body_dict = loads(body_str)

        # 获取数据
        username = body_dict.get('username')
        password = body_dict.get('password')
        password2 = body_dict.get('password2')
        mobile = body_dict.get('mobile')
        sms_code_cli = body_dict.get('sms_code')
        allow = body_dict.get('allow')
        redis_cli = get_redis_connection('code')
        sms_code_ser = redis_cli.get(mobile).decode()

        # 验证数据
        if not all([username, password, password2, mobile, allow]):
            return JsonResponse({"code": 400, "errmsg": "参数不全"})
        if not re.match('[a-zA-Z_-]{5,20}', username):
            return JsonResponse({"code": 400, "errmsg": "用户名格式错误"})
        elif User.objects.filter(username=username).count() != 0:
            return JsonResponse({"code": 400, "errmsg": "用户名重复"})
        if not re.match(r'\d{8,20}', password):
            return JsonResponse({"code": 400, "errmsg": "密码格式错误"})
        if not password2 == password:
            return JsonResponse({"code": 400, "errmsg": "验证密码与密码不同"})
        if not re.match(r'1[3-9]\d{9}', mobile):
            return JsonResponse({"code": 400, "errmsg": "电话号码格式错误"})
        elif User.objects.filter(mobile=mobile).count() != 0:
            return JsonResponse({"code": 400, "errmsg": "电话号重复"})
        if not sms_code_ser:
            return JsonResponse({"code": 400, "errmsg": "短信验证码已过期"})
        elif sms_code_cli != sms_code_ser:
            return JsonResponse({"code": 400, "errmsg": "短信验证码错误"})
        # if not re.match('[a-zA-Z_-]{5,20}', allow):
        #     return JsonResponse({"code": 400, "errmsg": ""})

        # 保存用户信息
        user = User.objects.create_user(username=username, password=password, mobile=mobile)
        
        # 实现状态保持
        login(request, user)

        return JsonResponse({"code": 0, "errmsg": "ok"})
