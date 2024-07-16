import os
from celery import Celery


# 配置环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'meiduo_mall.settings')
# 创建celery实例
app = Celery('celery_tasks')
# 设置broker
app.config_from_object('celery_tasks.config')

# 自动检测celery任务
app.autodiscover_tasks(['celery_tasks.sms.tasks'])
