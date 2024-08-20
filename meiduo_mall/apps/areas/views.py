from django.shortcuts import render
from django.http import JsonResponse
from django.views import View
from apps.areas.models import Area
from django.core.cache import cache

# Create your views here.
class AreaView(View):
    def get(self, request):
        # 查询数据
        province_list = cache.get('province')   # 先从缓存中查询

        if province_list is None:   # 缓存中没有就从数据库中查询
            provinces = Area.objects.filter(parent_id__isnull=True)
            # 查询结果是[QuerySet]类型，将数据转化
            province_list = []
            for province in provinces:
                province_list.append({"id": province.id, "name": province.name})
            # 将查询数据保存到缓存中
            cache.set('province', province_list, 3600*24)

            # 返回响应
            return JsonResponse({"code": 0, "errmsg": "ok", "province_list": province_list})
        else:
            return JsonResponse({"code": 0, "errmsg": "ok", "province_list": province_list})


class SubAreaView(View):
    def get(self, request, id):
        # 查询数据
        data_list = cache.get('city%s'%id)      # 先从缓存中查询
        if data_list is None:
            up_level = Area.objects.get(id=id)
            down_level = up_level.subs.all()
            # 查询结果是[QuerySet]类型，将数据转化
            data_list = []
            for i in down_level:
                data_list.append({"id": i.id, "name": i.name})
            # 将查询数据保存到缓存中
            cache.set('city%s'%id, data_list, 3600*24)

            # 返回响应
            return JsonResponse({"code": 0, "errmsg": "ok", "sub_data": {"subs": data_list}})
        else:
            return JsonResponse({"code": 0, "errmsg": "ok", "sub_data": {"subs": data_list}})
