import re
from django.shortcuts import render
from django.views import View
from QQLoginTool.QQtool import OAuthQQ
from django.http import JsonResponse
from django.contrib.auth import login
import json


# Create your views here.
class QQAuthURLView(View):
    def get(self, reauest):
        from meiduo_mall.settings import QQ_AppId, QQ_SecretId, redirect_uri


        # 实例化QQ登录工具
        qq_oauth = OAuthQQ(
            client_id=QQ_AppId,
            client_secret=QQ_SecretId,
            redirect_uri=redirect_uri,
            state='xxxx'
        )

        login_url = qq_oauth.get_qq_url()

        return JsonResponse({'code': 0, "errmsg": 'ok', "login_url": login_url})


class OauthQQView(View):
    def get(self, request):
            from meiduo_mall.settings import QQ_AppId, QQ_SecretId, redirect_uri
            from oauth.models import OAuthQQUser
            from apps.oauth.utils import generic_openid


            # 实例化QQ登录工具
            qq_oauth = OAuthQQ(
                client_id=QQ_AppId,
                client_secret=QQ_SecretId,
                redirect_uri=redirect_uri,
                state='xxxx'
            )

            # 获取并验证参数
            code = request.GET.get('code')
            if code is None:
                 return JsonResponse({"code": 400, 'errmsg': '参数不全'})
            
            # 获取token
            token = qq_oauth.get_access_token(code)
            # 获取openid
            openid = qq_oauth.get_open_id(token)

            # 根据openid进行查询
            try:
                qquser = OAuthQQUser.objects.get(openid=openid)
            # 判断用户不存在，发送信息让前端进行绑定
            except OAuthQQUser.DoesNotExist:
                # 加密openid
                openid = generic_openid(openid=openid)
                
                return JsonResponse({"code": 400, "access_token": openid})
            # 判断用户存在，直接登录
            else:
                login(request, qquser.user)
                response = JsonResponse({"code": 0, "errmsg": "ok"})
                response.set_cookie("username", qquser.user.username)

                return response
    
    def post(self, request):
        from apps.users.models import User
        from django_redis import get_redis_connection
        from oauth.models import OAuthQQUser
        from apps.oauth.utils import check_openid



        # 获取数据
        try:
            data = json.loads(request.body.decode())
        except Exception as e:
            return JsonResponse({"code": 400, "errmsg": "参数格式错误"})
        mobile = data.get('mobile')
        password = data.get('password')
        sms_code_cli = data.get('sms_code')
        openid = data.get('access_token')
        redis_cli = get_redis_connection('code')
        sms_code_ser = redis_cli.get(mobile)
        # 解密openid
        openid = check_openid(openid=openid)

        # 验证数据
        if not all([openid, password, mobile]):
            return JsonResponse({"code": 400, "errmsg": "参数不全"})
        if not re.match(r'\d{8,20}', password):
            return JsonResponse({"code": 400, "errmsg": "密码格式错误"})
        if not re.match(r'1[3-9]\d{9}', mobile):
            return JsonResponse({"code": 400, "errmsg": "电话号码格式错误"})
        if not sms_code_ser:
            return JsonResponse({"code": 400, "errmsg": "短信验证码已过期"})
        elif sms_code_cli != sms_code_ser.decode():
            return JsonResponse({"code": 400, "errmsg": "短信验证码错误"})
        
        # 根据手机号查询用户
        try:
            user = User.objects.get(mobile=mobile)
        except User.DoesNotExist:
            # 手机号不存在， 用户不存在，注册用户
            user = User.objects.create_user(username=mobile, mobile=mobile, password=password)
        else:
            # 手机号存在， 用户存在, 判断密码是否正确
            if not user.check_password(password):
                return JsonResponse({"code": 400, "errmsg": "用户名或密码错误"})
            
        # 绑定openid
        OAuthQQUser.objects.create(user=user, openid=openid)

        # 状态保持
        login(request, user)
        response = JsonResponse({"code": 0, "errmsg": "ok"})
        response.set_cookie('username', user.username)

        return response
