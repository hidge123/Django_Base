from django.shortcuts import render
from django.views import View
from apps.contents.models import ContentCategory
from utils.goods import get_categories

# Create your views here.
class IndexView(View):
    def get(self, request):
        # 获取首页分类数据
        categories = get_categories()
        # 获取首页广告数据
        contents = {}
        content_categories = ContentCategory.objects.all()
        for cat in content_categories:
            contents[cat.key] = cat.content_set.filter(status=True).order_by('sequence')

        # 渲染模板的上下文
        context = {
            'categories': categories,
            'contents': contents,
        }
        return render(request, 'index.html', context)
