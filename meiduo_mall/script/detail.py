#!/usr/bin/env python
import os
import sys
import django

# 获取当前脚本路径
script_path = os.path.dirname(os.path.abspath(__file__))

# 项目根目录路径
project_root = os.path.abspath(os.path.join(script_path, '../'))

# 将项目根目录添加到 sys.path
sys.path.insert(0, project_root)

# 设置 Django 配置文件
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "meiduo_mall.settings")

# 初始化 Django
try:
    django.setup()
    print("Django setup successful!")
except Exception as e:
    print(f"Error during Django setup: {e}")


from utils.goods import get_breadcrumb, get_categories, get_goods_specs
from apps.goods.models import SKU
from django.template import loader
from django.http import JsonResponse
from meiduo_mall.settings import BASE_DIR


def generitic_detail_html(sku_id):
    # SKU信息
    try:
        sku = SKU.objects.get(id=sku_id, is_launched=True)
    except SKU.DoesNotExist:
        return JsonResponse({"code": 400, "errmsg": "该数据不存在"})
    # 获取分类数据
    categories = get_categories()
    # 面包屑
    breadcrumb = get_breadcrumb(sku.category)
    # 规格信息
    goods_specs = get_goods_specs(sku=sku)

    # 渲染页面数据
    context = {
        'categories': categories,
        'breadcrumb': breadcrumb,
        'sku': sku,
        'specs': goods_specs
    }

    # 获取模板
    detail_template = loader.get_template('detail.html')
    # 将数据给模板
    rendered_template = detail_template.render(context=context)

    # 将渲染好的模板写入到指定路径
    file_path = os.path.join(os.path.dirname(BASE_DIR), 'front_end_pc/goods/%s.html'%sku_id)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(rendered_template)
    
    print(sku_id)

skus = SKU.objects.all()
for sku in skus:
    generitic_detail_html(sku.id)
