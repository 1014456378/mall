import random
import logging
from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
from rest_framework.response import Response
from rest_framework.views import APIView
from meiduo_mall.libs.captcha.captcha import captcha
from django_redis import get_redis_connection
from . import constants
from .serializers import CheckImageCodeSerializer
from meiduo_mall.libs.yuntongxun.sms import CCP
logger = logging.getLogger('django')
#GET /image_code/(?P<image_code_id>[\w-]+)/
class ImageCodeView(APIView):
    """
    图片验证码
    1.使用captcha生成图片验证码
    2.使用redis保存图片验证码文本，以uuid为key，以验证码文本为value
    3.返回验证码图片
    """
    def get(self,request,image_code_id):
        text,image = captcha.generate_captcha()
        logger.info('图片验证码为%s' %text)
        redis_conn = get_redis_connection('verify_codes')
        redis_conn.setex('img_%s' %image_code_id,constants.IMAGE_CODE_REDIS_EXPIRES,text)
        return HttpResponse(image,content_type='image/jpg')

#GET /sms_codes/(?P<mobile>1[3-9]\d{9})/?image_code_id=xxx&text=xxx
class SMSCodeView(APIView):
    """
    短信验证码
    1.获取参数进行校验（参数完整性，图片验证码是否正确）
    2.发送短信验证码
    3.返回应答
    """
    def get(self,request,mobile):
        serializer = CheckImageCodeSerializer(data=request.query_params,context={'mobile':mobile})
        serializer.is_valid(raise_exception=True)
        sms_code = '%06d'%random.randint(0,999999)
        logger.info('短信验证码为：%s' %sms_code)
        redis_conn = get_redis_connection('verify_codes')
        #redis管道
        pipeline = redis_conn.pipeline()
        pipeline.setex('sms_%s'%mobile,constants.SMS_CODE_REDIS_EXPIRES,sms_code)
        #存入规定时间内生效的电话标记，防止频繁发送短信,在序列化器中进行验证
        pipeline.setex('send_flag_%s' %mobile,constants.SEND_SMS_CODE_INTERVAL,1)
        #一次性执行管道所有操作
        pipeline.execute()
        expires = constants.SMS_CODE_REDIS_EXPIRES // 60
        from celery_tasks.sms.tasks import send_sms_code
        send_sms_code.delay(mobile,sms_code,expires)
        return Response({'message':'发送短信成功'})



