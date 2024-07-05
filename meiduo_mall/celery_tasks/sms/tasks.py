from random import randint
from celery_tasks.main import app
from libs.yuntongxun.sms import CCP
from django_redis import get_redis_connection


# 装饰任务
@app.task(name='send_sms_code')
def send_sms_code(mobile: str):
        # 链接redis
        redis_cli = get_redis_connection('code')
        # 生成短信验证码
        sms_code = '%04d' % randint(0, 9999)
        # 保存短信验证码
        pipeline = redis_cli.pipeline()
        pipeline.setex(mobile, 300, sms_code)
        # 添加发送标记
        pipeline.setex('send_flag_%s' % mobile, 60, 1)
        # 执行
        pipeline.execute()
        # 发送短信验证码
        CCP().send_template_sms(mobile, [sms_code, 5], 1)
