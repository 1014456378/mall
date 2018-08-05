from django.core.mail import send_mail
from django.conf import settings
from celery_tasks.main import celery_app
import logging
logger = logging.getLogger('django')
@celery_app.task(name='send_verifyemail')
def send_verify_email(to_email,verify_url):
    """
        发送验证邮箱邮件
        to_email: 收件人邮箱
        verify_url: 验证链接
        return: None
    """
    subject = '美多商城邮箱验证'
    html_message = '<p>尊敬的用户您好！</p>' \
                   '<p>感谢您使用美多商城。</p>' \
                   '<p>您的邮箱为：%s 。请点击此链接激活您的邮箱：</p>' \
                   '<p><a href="%s">%s<a></p>' % (to_email, verify_url, verify_url)
    logger.error("发送验证码邮件被调用")
    try:
        send_mail(subject,'',settings.EMAIL_FROM,[to_email],html_message=html_message)
    except Exception as e:
        logger.error("发送验证码邮件[异常][ email: %s, message: %s ]" % (to_email, e))

#启动worker celery -A celery_tasks.main worker --loglevel=info


