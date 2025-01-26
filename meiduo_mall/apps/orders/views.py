from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from apps.areas.models import Address
from django_redis import get_redis_connection
from apps.goods.models import SKU

# Create your views here.
class OrderSettlementView(LoginRequiredMixin, View):
    """订单结算"""

    def get(self, request):
        from decimal import Decimal


        # 获取用户信息
        user = request.user

        # 获取用户地址信息
        addresses = Address.objects.filter(user=user, is_deleted=False)
        # 将对象数据转化为字典数据
        address_list = []
        for address in addresses:
            address_list.append({
                'id':address.id,
                'province':address.province.name,
                'city':address.city.name,
                'district':address.district.name,
                'place':address.place,
                'receiver':address.receiver,
                'mobile':address.mobile
            })
        
        # 获取用户商品数据
        redis_cli = get_redis_connection('cart')
        pipeline = redis_cli.pipeline()
        pipeline.hgetall("carts_%s"%user.id)
        pipeline.smembers("selected_%s"%user.id)
        result = pipeline.execute()

        # 从redis中查询被选中的商品信息
        sku_count = result[0]
        selected_list = result[1]
        cart = {}
        for sku_id in selected_list:
            cart[int(sku_id)] = int(sku_count[sku_id])
        
        # 查询商品信息并整理为字典格式
        sku_list = []
        skus = SKU.objects.filter(id__in=cart.keys())
        for sku in skus:
            sku_list.append({
                'id':sku.id,
                'name':sku.name,
                'default_image_url':sku.default_image.url,
                'count': cart[sku.id],
                'price':sku.price
            })
        
        # 返回响应
        freight = Decimal(10)
        context = {"skus": sku_list, "addresses": address_list, "freight": freight}

        return JsonResponse({"code": 0, "errmsg": "ok", "context": context})
