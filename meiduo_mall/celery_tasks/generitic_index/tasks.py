from django.template import loader
from os import path
from apps.contents.models import ContentCategory
from utils.goods import get_categories
from meiduo_mall.settings import BASE_DIR
from celery_tasks.main import app


@app.task(name='genertic_meiduo_index')
def genertic_meiduo_index():
    # 获取分类数据
    categories = get_categories()

    # 首页广告数据
    contents = {}
    content_categories = ContentCategory.objects.all()
    for cat in content_categories:
        contents[cat.key] = cat.content_set.filter(status=True).order_by('sequence')
    
    # 渲染模板的上下文
    context = {
        'categories': categories,
        'contents': contents,
    }
    
    # 加载渲染的模板
    index_template = loader.get_template('index.html')
    # 将数据给模板
    rendered_template = index_template.render(context=context)

    # 将渲染好的模板写入指定文件
    file_path = path.join(path.dirname(BASE_DIR), 'front_end_pc/index.html')
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(rendered_template)
