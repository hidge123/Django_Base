from django.shortcuts import render
from django.http import JsonResponse
from django.views import View
from apps.areas.models import Area

# Create your views here.
class AreaView(View):
    def get(self, request):
        # 查询数据
        provinces = Area.objects.filter(parent_id__isnull=True)
        # 查询结果是[QuerySet]类型，将数据转化
        province_list = []
        for province in provinces:
            province_list.append({"id": province.id, "name": province.name})

        # 返回响应
        return JsonResponse({"code": 0, "errmsg": "ok", "province_list": province_list})


class SubAreaView(View):
    def get(self, reques, id):
        # 查询数据
        up_level = Area.objects.get(id=id)
        down_level = up_level.subs.all()
        # 查询结果是[QuerySet]类型，将数据转化
        data_list = []
        for i in down_level:
            data_list.append({"id": i.id, "name": i.name})

        # 返回响应
        return JsonResponse({"code": 0, "errmsg": "ok", "sub_data": {"subs": data_list}})
