from django.shortcuts import render
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse


# Create your views here.
class PayUrlVIew(View):
    """生成支付链接"""
    def get(self, request, order_id):
        from apps.orders.models import OrderInfo
        from alipay import AliPay, AliPayConfig


        user =request.user

        # 验证订单id
        try:
            order_info = OrderInfo.objects.get(
                order_id = order_id,
                status = OrderInfo.ORDER_STATUS_ENUM['UNPAID'],
                user = user
            )
        except OrderInfo.DoesNotExist:
            return JsonResponse({"code": 400, "errmsg": "订单不存在"})
        
        # 读取应用私钥和支付宝公钥
        from meiduo_mall.settings import ALIPAY_PUBLIC_KEY_PATH, APP_PRIVATE_KEY_PATH
        app_private_key_string = open(APP_PRIVATE_KEY_PATH).read()
        alipay_public_key_string = open(ALIPAY_PUBLIC_KEY_PATH).read()

        # 创建支付宝实列
        from meiduo_mall.settings import ALIPAY_APPID, ALIPAY_RETURN_URL, ALIPAY_DEBUG, ALIPAY_URL
        alipay = AliPay(
                appid=ALIPAY_APPID,
                app_notify_url=None,  # 默认回调 url
                app_private_key_string=app_private_key_string,
                alipay_public_key_string=alipay_public_key_string,
                sign_type="RSA2",  # RSA 或者 RSA2
                debug=ALIPAY_DEBUG,  # 默认 False
                verbose=False,  # 输出调试数据
                config=AliPayConfig(timeout=15)  # 可选，请求超时时间
        )

        # 调用支付宝方法
        subject = "美多商城测试订单"
        # 电脑网站支付
        order_string = alipay.api_alipay_trade_page_pay(
            out_trade_no=order_info.order_id,
            total_amount=str(order_info.total_amount),
            subject=subject,
            return_url=ALIPAY_RETURN_URL,
            notify_url="" # 可选，不填则使用默认 notify url
        )

        # 拼接跳转链接
        alipay_url = ALIPAY_URL + "?" + order_string
        # 返回响应
        return JsonResponse({"code": 0, "errmsg": "ok", "alipay_url": alipay_url})
