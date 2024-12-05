from celery.schedules import crontab
import os
from meiduo_mall.settings import BASE_DIR


broker_url = 'redis://127.0.0.1/15'

beat_schedule = {
    'genertic-every-60-seconds': {
        'task': 'genertic_meiduo_index',
        'schedule': crontab(minute='*/1')
    },
}
timezone = 'UTC'

beat_schedule_filename = os.path.join(BASE_DIR, 'celery_tasks/celery_beat_schedule/')
