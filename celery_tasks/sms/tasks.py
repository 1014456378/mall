from celery_tasks.main import celery_app


#定义任务函数
@celery_app.task(name='send_sms_code')
def send_sms_code(a,b):
    pass