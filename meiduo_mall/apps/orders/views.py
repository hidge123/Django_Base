from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from apps.areas.models import Address
from django_redis import get_redis_connection
from apps.goods.models import SKU
import json

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
        carts = {}
        for sku_id in selected_list:
            carts[int(sku_id)] = int(sku_count.get(sku_id))
        
        # 查询商品信息并整理为字典格式
        sku_list = []
        skus = SKU.objects.filter(id__in=carts.keys())
        for sku in skus:
            sku_list.append({
                'id': sku.id,
                'name': sku.name,
                'default_image_url': sku.default_image.url,
                'count': carts.get(sku.id),
                'price': sku.price
            })
        
        # 返回响应
        freight = Decimal(10)
        context = {"skus": sku_list, "addresses": address_list, "freight": freight}

        return JsonResponse({"code": 0, "errmsg": "ok", "context": context})


class OrderCommitView(LoginRequiredMixin, View):
    """订单提交"""
    def post(self, request):
        from apps.orders.models import OrderInfo, OrderGoods
        from decimal import Decimal
        from django.utils import timezone
        from django.db import transaction


        user = request.user
        data = json.loads(request.body.decode())
        address_id = data.get('address_id')
        pay_method = data.get('pay_method')

        # 验证数据
        if not all([address_id, pay_method]):
            return JsonResponse({"code": 400, "errmsg": "参数不全"})
        try:
            address = Address.objects.get(id=address_id)
        except Address.DoesNotExist:
            return JsonResponse({"code": 400, "errmsg": "地址信息错误"})
        if pay_method not in (OrderInfo.PAY_METHODS_ENUM['CASH'], OrderInfo.PAY_METHODS_ENUM['ALIPAY']):
            return JsonResponse({"code": 400, "errmsg": "支付方法错误"})
        
        # 保存订单基本信息
        order_id = timezone.localtime().strftime(r'%Y%m%d%H%M%S') + '%09d'%user.id
        # 根据用户支付方式生成支付状态
        if pay_method == OrderInfo.PAY_METHODS_ENUM['CASH']:
            status = OrderInfo.ORDER_STATUS_ENUM['UNSEND']  # 货代付款
        else:
            status = OrderInfo.ORDER_STATUS_ENUM['UNPAID']  # 支付宝支付
        # 生成总金额和总商品数（暂时）
        total_count = 0
        total_amount = Decimal('0')
        freight = Decimal('10.00')  # 运费

        with transaction.atomic():
            point = transaction.savepoint()     # 事务的起始点

            orderinfo = OrderInfo.objects.create(
                order_id = order_id,
                user = user,
                address = address,
                total_amount = total_amount,
                total_count = total_count,
                freight = freight,
                pay_method = pay_method,
                status = status
            )

            # 保存订单商品信息
            # 获取redis中的数据
            redis_cli = get_redis_connection('cart')
            pipeline = redis_cli.pipeline()
            pipeline.hgetall('carts_%s'%user.id)
            pipeline.smembers('selected_%s'%user.id)
            sku_id_counts, selected_ids = pipeline.execute()

            # 重新组织选中的商品信息
            carts = {}
            for sku_id in selected_ids:
                carts[int(sku_id)] = int(sku_id_counts.get(sku_id))
            
            # 查询商品信息并保存入库
            for sku_id, count in carts.items():
                sku = SKU.objects.get(id=sku_id)
                # 判断商品库存是否充足
                if sku.stock < count:
                    transaction.savepoint_rollback(point)   # 事务的回滚点
                    return JsonResponse({"code": 400, "errmsg": "商品不足，下单失败"})
                else:
                    sku.stock -= count  # 更新库存
                    sku.sales += count  # 更新销量
                    sku.save()

                    # 更新商品总数和总金额
                    orderinfo.total_amount += (sku.price*count)
                    orderinfo.total_count += count
                    
                    # 订单商品信息数据入库
                    OrderGoods.objects.create(
                        order = orderinfo,
                        sku = sku,
                        count = count,
                        price = sku.price
                    )
            orderinfo.save()
            transaction.savepoint_commit(point)     # 事务的提交点
        
        # 从redis中移除已提交的商品
        pipeline.hdel('carts_%s' % user.id, *selected_ids)
        pipeline.srem('carts_%s' % user.id, *selected_ids)
        pipeline.execute()

        # 返回响应
        return JsonResponse({"code": 0, "errmsg": "ok", "order_id": order_id})
