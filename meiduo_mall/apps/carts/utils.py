import pickle, base64
from apps.goods.models import SKU
from django.http import JsonResponse
from django_redis import get_redis_connection
import logging


def merge_cookie_to_redis(request, response):
    """合并cookie数据到redis中"""

    logger = logging.getLogger('django')

    # 读取cookie数据
    cookie_carts = request.COOKIES.get('carts')

    if cookie_carts is not None:
        # 解密数据
        carts = pickle.loads(base64.b64decode(cookie_carts))
        # 验证数据
        sku_ids = carts.keys()
        for sku_id in sku_ids:
            try:
                SKU.objects.get(id=sku_id)
            except:
                logger.error(f"Error occurred: {e}")
                del carts[sku_id]

        # 初始化
        cookie_dict = {}
        selected_ids = []
        unselected_ids = []

        # 遍历商品数据
        for sku_id, count_selected_dict in carts.items():
            # 整理数据格式
            try:
                count = int(count_selected_dict['count'])
                cookie_dict[sku_id] = count
            except Exception as e:
                logger.error(f"Error occurred: {e}")

            if type(count_selected_dict['selected']) != bool:
                logger.error(f"Error occurred: {e}")
            elif count_selected_dict['selected']:
                selected_ids.append(sku_id)
            else:
                unselected_ids.append(sku_id)

        # 将数据添加到redis中
        redis_cli = get_redis_connection('cart')
        pipeline = redis_cli.pipeline()
        user = request.user
        pipeline.hmset('carts_%s'%user.id, cookie_dict)
        if len(selected_ids) > 0:
            pipeline.sadd('selected_%s'%user.id, *selected_ids)
        if len(unselected_ids) > 0:
            pipeline.srem('selected_%s'%user.id, *unselected_ids)
        pipeline.execute()

        # 设置cookie并返回响应
        response.delete_cookie('carts')

        return response
    
    else:
        return response
