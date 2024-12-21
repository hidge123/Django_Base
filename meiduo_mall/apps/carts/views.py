from django.shortcuts import render
from django.http import JsonResponse
from django.views import View
from json import loads
from apps.goods.models import SKU
from django_redis import get_redis_connection
import pickle, base64

# Create your views here.
class CartView(View):
    """购物车视图"""
    def post(self, request):
        """
        添加购物车
        """
        # 获取参数
        data = loads(request.body.decode())
        sku_id = data.get('sku_id')
        count = data.get('count')
        # 验证参数
        try:
            SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            return JsonResponse({"code": 400, "errmsg": "没有该商品"})
        try:
            count = int(count)
        except:
            count = 1
        
        # 判断用户是否登录
        user = request.user
        # is_authenticated方法能判断用户是否是验证用户
        if user.is_authenticated:
            # 登录用户将数据存储在redis中
            redis_cli = get_redis_connection('cart')
            redis_cli.hset('cart_%s'%user.id, sku_id, count)
            # 保存选中状态(默认就是选中状态)
            redis_cli.sadd('selected_%s'%user.id, sku_id)

            # 返回响应
            return JsonResponse({"code": 0, "errmsg": "ok"})
        else:
            # 未登录用户存储在cookie中
            # 获取cookie
            cookie_carts = request.COOKIES.get('carts')

            # 判断cookie是否存在
            if cookie_carts:
                # 有数据就进行解密
                carts = pickle.loads(base64.b64decode(cookie_carts))

                # 判断数据是否已存在
                if sku_id in carts:
                    # 存在就更新数据
                    count += carts[sku_id]["count"]

                carts[sku_id] = {"count": count, "selected": True}
            else:
                # 没有就进行初始化
                carts = {sku_id: {"count": count, "selected": True}}

            # 用pickle和base64对其进行加密
            carts_bits = pickle.dumps(carts)  # 将python字典序化为二进制类型数据
            carts_bits = base64.b64encode(carts_bits)    # 将二进制数据重新编码为base64格式
            # 设置cookie
            response = JsonResponse({"code": 0, "errmsg": "ok"})
            # 由于cookie的value参数必须是str类型，所以必须对其解码
            response.set_cookie("carts", carts_bits.decode(), 3600*24*12)

            # 返回响应
            return response
