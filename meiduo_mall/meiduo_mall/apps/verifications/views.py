from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from meiduo_mall.libs.captcha.captcha import captcha
from django_redis import get_redis_connection
from . import constants
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
        redis_conn = get_redis_connection('verify_codes')
        redis_conn.setex('img_%s' %image_code_id,constants.IMAGE_CODE_REDIS_EXPIRES,text)
        return HttpResponse(image,content_type='image/jpg')
