from json import loads
from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
from apps.users.models import User
from django_redis import get_redis_connection
import re
from django.contrib.auth.mixins import LoginRequiredMixin


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
        from django.contrib.auth import login


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
        sms_code_ser = redis_cli.get(mobile)

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
        elif sms_code_cli != sms_code_ser.decode():
            return JsonResponse({"code": 400, "errmsg": "短信验证码错误"})

        # 保存用户信息
        user = User.objects.create_user(username=username, password=password, mobile=mobile)
        
        # 实现状态保持
        login(request, user)

        return JsonResponse({"code": 0, "errmsg": "ok"})


class LoginView(View):
    def post(self, request):
        from django.contrib.auth import authenticate, login


        # 获取数据
        data = loads(request.body.decode())
        username = data.get('username')
        password = data.get('password')
        remembered = data.get('remembered')

        # 验证数据
        if not all([username, password]):
            return JsonResponse({"code": 400, "errmsg": "参数不全"})
        # 判断用户名类型
        if re.match(r'1[3-9]\d{9}', username):
            User.USERNAME_FIELD = 'mobile'
        else:
            User.USERNAME_FIELD = 'username'
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
        else:
            return JsonResponse({"code": 400, "errmsg": "用户名或密码错误"})
        
        # 判断是否记住登录
        if remembered:
            request.session.set_expiry(None)
        else:
            request.session.set_expiry(0)

        # 返回响应
        response = JsonResponse({"code": 0, "errmsg": "ok"})
        response.set_cookie('username', username)

        return response


class LogoutView(View):
    def delete(self, request):
        from django.contrib.auth import logout


        logout(request)
        response = JsonResponse({"code": 0, "errmsg": "ok"})
        response.delete_cookie('username')

        return response


class CenterView(LoginRequiredMixin, View):
    # 重写了父类的dispatch方法
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({"code": 400, "errmsg": "用户未登录"})
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        info_data = {
            'username': request.user.username,
            'mobile': request.user.mobile,
            'email': request.user.email,
            'email_active': request.user.email_active
        }

        return JsonResponse({"code": 0, "errmsg": "ok", 'info_data': info_data})


class EmailView(LoginRequiredMixin, View):
    def put(self, request):
        from apps.users.utils import generic_email_verify_token
        from celery_tasks.send_email.tasks import celery_send_email


        # 接受请求
        data = loads(request.body.decode())
        # 获取数据
        email = data.get('email')
        # 验证数据
        if email is None:
            return JsonResponse({"code": 400, "errmsg": "参数不全"})
        result = re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email)
        if result is None:
            return JsonResponse({"code": 400, "errmsg": "邮箱格式错误"})

        # 保存邮箱地址
        user = request.user     # 获取用户信息
        # 判断用户邮箱是否已经存在
        if not user.email is None:
            pass
        elif user.email == email:
            pass
        else:
            user.email = email
            user.save()

        # 发送激活邮件
        subject = '美多商城激活邮件'        # 主题
        message = ''        # 内容
        from_email = '美多商城<charliemorningstar@163.com>'     # 发件人
        recipient_list = ['charliemorningstar@163.com']      # 收件人列表
        token = generic_email_verify_token(user.id)
        celery_send_email.delay(subject=subject, message=message, from_email=from_email, recipient_list=recipient_list, token=token)

        # 返回响应
        return JsonResponse({"code": 0, "errmsg": "ok"})
