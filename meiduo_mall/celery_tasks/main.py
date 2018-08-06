from celery import Celery
# 为celery使用django配置文件进行设置
import os
if not os.getenv('DJANGO_SETTINGS_MODULE'):
    os.environ['DJANGO_SETTINGS_MODULE'] = 'meiduo_mall.settings.dev'
#创建Celery类的对象

# celery_app = Celery('celery_tasks',broker='redis://127.0.0.1:6379/3')
celery_app = Celery('meiduo')
#加载配置
celery_app.config_from_object('celery_tasks.config')
#自动加载任务
celery_app.autodiscover_tasks(['celery_tasks.sms','celery_tasks.email'])


#启动worker celery -A celery_tasks.main worker --loglevel=info
