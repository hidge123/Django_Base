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
            pipline = redis_cli.pipeline()
            pipline.hincrby('carts_%s'%user.id, sku_id, count)
            # 保存选中状态(默认就是选中状态)
            pipline.sadd('selected_%s'%user.id, sku_id)
            pipline.execute()

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
                    count += carts.get(sku_id).get("count")

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
    
    def get(self, request):
        """
        查询购物车
        """
        # 判断用户是否登录
        user = request.user
        if user.is_authenticated:
            # 登录用户从redis中获取数据
            redis_cli = get_redis_connection('cart')
            sku_id_count = redis_cli.hgetall('carts_%s'%user.id)
            selected_ids = redis_cli.smembers('selected_%s'%user.id)
            # 将数据转化为字典格式
            carts = {}
            for sku_id, count in sku_id_count.items():
                carts[int(sku_id)] = {"count": int(count), "selected": sku_id in selected_ids}

        else:
            # 未登录用户从cookie中获取数据
            cookie_carts = request.COOKIES.get('carts')
            # 判断字典数据是否存在
            if cookie_carts is not None:
                # 有就查询数据
                # 对数据进行解密
                carts = pickle.loads(base64.b64decode(cookie_carts))

            else:
                # 未存在就初始化一个空字典
                carts = {}
                return JsonResponse({"code": 0, "errmsg": "ok", "cart_skus": []})

        # 查询商品数据
        sku_ids = carts.keys()
        skus = SKU.objects.filter(id__in=sku_ids)
        # 将数据转化为字典数据
        sku_list = []
        for sku in skus:
            sku_list.append({
            'id': sku.id, 'name': sku.name, 'price': sku.price, 'default_image_url': sku.default_image.url,
            'selected': carts[sku.id]['selected'], 'count': carts[sku.id]['count'], 'amount': sku.price*carts[sku.id]['count']
            })

        # 返回响应
        return JsonResponse({"code": 0, "errmsg": "ok", "cart_skus": sku_list})
    
    def put(self, request):
        """
        修改购物车
        """

        # 获取数据
        user = request.user
        data = loads(request.body.decode())
        sku_id = data.get('sku_id')
        count = data.get('count')
        selected = data.get('selected')

        # 验证数据
        if not all([sku_id, count]):
            return JsonResponse({"code": 400, "errmsg": "参数不全"})
        if type(selected) != bool:
            return JsonResponse({"code": 400, "errmsg": "数据类型错误"})
        try:
            SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            return JsonResponse({"code": 400, "errmsg": "该商品不存在"})
        try:
            count = int(count)
        except:
            return JsonResponse({"code": 400, "errmsg": "数据类型错误"})

        # 判断用户是否登录
        if user.is_authenticated:
            # 登录用户更新redis
            redis_cli = get_redis_connection('cart')
            pipeline = redis_cli.pipeline()
            pipeline.hset('carts_%s'%user.id, sku_id, count)
            if selected:
                pipeline.sadd('selected_%s'%user.id, sku_id)
                pipeline.execute()
            else:
                pipeline.srem('selected_%s'%user.id, sku_id)
                pipeline.execute()

            # 返回响应
            return JsonResponse({"code": 0, "errmsg": "ok", "cart_sku": {"count": count, "selected": selected}})

        else:
            # 未登录用户更新cookie
            cookie_carts = request.COOKIES.get('carts')
            # 判断是否有cookie数据
            if cookie_carts is not None:
                carts = pickle.loads(base64.b64decode(cookie_carts))
            else:
                # 没有cookie数据就初始化
                carts = {}
            
            # 更新数据
            if sku_id in carts:
                carts[sku_id] = {'count': count, 'selected': selected}
            # 加密数据
            carts = base64.b64encode(pickle.dumps(carts))
            
            # 设置cookie并返回响应
            response = JsonResponse({"code": 0, "errmsg": "ok", "cart_sku": {"count": count, "selected": selected}})
            response.set_cookie('carts', carts.decode(), max_age=14*24*3600)
            return response

    def delete(self, request):
        """购物车删除"""
        # 获取并验证数据
        data = loads(request.body.decode())
        sku_id = data.get('sku_id')
        try:
            SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            return JsonResponse({"code": 400, "errmsg": "没有此商品"})
        
        # 判断用户是否登录
        user = request.user
        if user.is_authenticated:
            # 登录用户操作redis
            redis_cli = get_redis_connection('cart')
            pipeline = redis_cli.pipeline()
            pipeline.hdel('carts_%s'%user.id, sku_id)  # 删除hash表中数据
            pipeline.srem('selected_%s'%user.id, sku_id)   # 删除选中状态
            pipeline.execute()

            return JsonResponse({"code": 0, "errmsg": "ok"})
        
        else:
            # 未登录用户操作cookie
            cookie_carts = request.COOKIES.get('carts')
            # 判断是否有cookie数据
            if cookie_carts is not None:
                # 有就解密数据
                carts = pickle.loads(base64.b64decode(cookie_carts))
            else:
                # 没有cookie数据就初始化
                carts = {}
            
            # 删除数据
            del carts[sku_id]
            # 加密数据
            carts = base64.b64encode(pickle.dumps(carts))
            # 设置cookie
            response = JsonResponse({"code": 0, "errmsg": "ok"})
            response.set_cookie('carts', carts.decode(), max_age=14*24*3600)

            # 返回响应
            return response


class CartSimpleView(View):
    """商品页面右上角购物车简单展示"""
    def get(self, request):
        # 判断用户登录状态
        user = request.user
        if user.is_authenticated:
            # 获取redis中的数据
            redis_cli = get_redis_connection('cart')
            pipeline = redis_cli.pipeline()
            pipeline.hgetall('carts_%s'%user.id)
            pipeline.smembers('selected_%s'%user.id)
            result = pipeline.execute()

            # 将查询到的数据与redis中的数据格式统一
            if len(result) == 2:
                sku_count = result[0]
                selected_ids = result[1]
                carts = {}

                for sku_id, count in sku_count.items():
                    carts[int(sku_id)] = {'count': int(count), 'selected': sku_id in selected_ids}

            else:
                carts = {}

        else:
            # 获取cookie数据
            cookie_carts = request.COOKIES.get('carts')
            # 判断cookie中的数据是否存在
            if cookie_carts is not None:
                # 解密数据
                carts = pickle.loads(base64.b64decode(cookie_carts))
            
            else:
                # 没有就初始化
                carts = {}
        
        # 将查询到的数据整理为列表格式返回
        cart_skus = []
        # 验证sku数据
        for sku_id in carts.keys():
            try:
                SKU.objects.get(id=sku_id)
            except:
                del carts[sku_id]
        
        skus = SKU.objects.filter(id__in=carts.keys())
        for sku in skus:
            cart_skus.append({"id": sku.id, "name": sku.name, "default_image_url": sku.default_image.url, "count": carts.get(sku.id).get("count")})

        return JsonResponse({"code": 0, "errmsg": "ok", "cart_skus": cart_skus})
