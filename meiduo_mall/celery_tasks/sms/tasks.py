from celery_tasks.main import celery_app
from .yuntongxun.sms import CCP
import logging
logger = logging.getLogger('django')
SMS_CODE_TEMP_ID = 1

#定义任务函数
@celery_app.task(name='send_sms_code')
def send_sms_code(mobile,sms_code,expires):
    print('发送短信的任务被调用：mobile：%s sms_code:%s'%(mobile,sms_code))
    try:
        ccp = CCP()
        result = ccp.send_template_sms(mobile, [sms_code, expires], SMS_CODE_TEMP_ID)
    except Exception as e:
        logger.error("发送验证码短信[异常][ mobile: %s, message: %s ]" % (mobile, e))
    else:
        if result == 0:
            logger.info("发送验证码短信[正常][ mobile: %s ]" % mobile)
        else:
            logger.warning("发送验证码短信[失败][ mobile: %s ]" % mobile)