from celery import Celery

#创建Celery类的对象

# celery_app = Celery('celery_tasks',broker='redis://127.0.0.1:6379/3')
celery_app = Celery('celery_tasks')
#加载配置
celery_app.config_from_object('celery_tasks.config')
#自动加载任务
celery_app.autodiscover_tasks(['celery_tasks.sms'])


