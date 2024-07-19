from django.shortcuts import render
from django.views import View
from QQLoginTool.QQtool import OAuthQQ
from django.http import JsonResponse

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
