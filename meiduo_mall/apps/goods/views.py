from django.shortcuts import render
from fastdfs_client.client import FastdfsClient
from django.views import View
from django.http import HttpResponse, JsonResponse

# Create your views here.
class ListView(View):
    """商品数据的展示"""
    def get(self, request, category_id):
        from apps.goods.models import GoodsCategory, SKU
        from utils.goods import get_breadcrumb
        from django.core.paginator import Paginator, EmptyPage


        # 获取参数
        page = request.GET.get("page")
        ordering = request.GET.get("ordering")
        page_size = request.GET.get("page_size")

        # 根据分类id查询分类数据
        try:
            category = GoodsCategory.objects.get(id=category_id)
        except GoodsCategory.DoesNotExist:
            return JsonResponse({"code":400, "errmsg":"获取mysql数据出错"})
        
        # 获取面包屑数据
        breadcrumb = get_breadcrumb(category)

        # 查询分类对应的sku数据，再将其排序，分页
        try:
            skus = SKU.objects.filter(category=category, is_launched=True).order_by(ordering)
        except SKU.DoesNotExist:
            return JsonResponse({"code":400, "errmsg":"获取mysql数据出错"})
        paginator = Paginator(skus, page_size)

        # 获取每商品数据
        try:
            page_skus = paginator.page(page)
        except EmptyPage:
            return JsonResponse({'code':400,'errmsg':'page数据出错'})
        # 获取当前总页数
        total_num = paginator.num_pages

        # 将数据转换为对应格式
        sku_list = []
        for sku in page_skus:
            sku_list.append({"name": sku.name, 'id': sku.id, 'default_image_url': sku.default_image.url, 'price': sku.price})
        # 返回响应
        return JsonResponse({'code': 0, 'errmsg':'ok', 'breadcrumb': breadcrumb, 'list':sku_list, 'count': total_num})


class HotGoodsView(View):
    """热销商品的展示"""
    def get(slef, request, category_id):
        from apps.goods.models import SKU


        # 获取热销商品数据
        try:
            skus = SKU.objects.filter(category_id=category_id, is_launched=True).order_by('-sales')[:2]
        except SKU.DoesNotExist:
            return JsonResponse({"code":400, "errmsg":"获取mysql数据出错"})
        
        # 将数据转化为对应格式
        hot_skus = []
        for sku in skus:
            hot_skus.append({'id': sku.id, 'default_image_url': sku.default_image.url, "name": sku.name, "price": sku.price})
        
        # 返回响应
        return JsonResponse({"code": 0, "errmsg": "ok", "hot_skus": hot_skus})
