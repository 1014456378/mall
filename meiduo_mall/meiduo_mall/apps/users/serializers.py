import re
from django_redis import get_redis_connection
from rest_framework import serializers

from goods.models import SKU
from . import constants
from .models import User
from rest_framework_jwt.settings import api_settings
from celery_tasks.email.tasks import send_verify_email

class CreateUserSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(label='确认密码',write_only=True)
    sms_code = serializers.CharField(label='短信验证码',write_only=True)
    allow = serializers.CharField(label='同意协议',write_only=True)
    token = serializers.CharField(label='登陆状态token',read_only=True)
    class Meta:
        model = User
        fields = ('id','username','mobile','password','password2','sms_code','allow','token')
        extra_kwargs = {
            'username':{
                'min_length':5,
                'max_length':20,
                'error_messages':{
                    'min_length':'仅允许5-20个字符的用户名',
                    'max_length':'仅允许5-20个字符的用户名',
                }
            },
            'password':{
                'write_only':True,
                'min_length':8,
                'max_length':20,
                'error_messages':{
                    'min_length': '仅允许8-20个字符的密码',
                    'max_length': '仅允许8-20个字符的密码',
                }
            }
        }
    def validate_mobile(self,value):
        if not re.match(r'^1[3-9]\d{9}$',value):
            raise serializers.ValidationError('手机号格式错误')
        return value
    def validate_allow(self, value):
        if value!='true':
            raise serializers.ValidationError('请同意用户协议')
        return value
    def validate(self, data):
        if data['password']!=data['password2']:
            raise serializers.ValidationError('两次密码不一样')
        redis_conn = get_redis_connection('verify_codes')
        real_sms_code = redis_conn.get('sms_%s' %data['mobile'])
        if real_sms_code is None:
            raise serializers.ValidationError('无效的短信验证码')
        if real_sms_code.decode()!=data['sms_code']:
            raise serializers.ValidationError('短信验证码错误')
        return data
    def create(self, validated_data):
        del validated_data['sms_code']
        del validated_data['password2']
        del validated_data['allow']
        user = super().create(validated_data)
        user.set_password(validated_data['password'])
        user.save()

        #使用jwt产生token
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)
        user.token = token
        return user

#用户信息的序列化器
class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id','username','mobile','email','email_active')

#发送邮件接口
class EmailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id','email')
        extra_kwargs = {
            'email':{
                'required':True
            }
        }
    def update(self, instance, validated_data):
        email = validated_data['email']
        instance.email = validated_data['email']
        instance.save()
        verify_url = instance.generate_verify_email_url()
        send_verify_email.delay(email,verify_url)
        return instance

class AddUserBrowsingHistorySerializer(serializers.Serializer):
    sku_id = serializers.IntegerField(label='商品sku编号',min_value=0)
    def validate_sku_id(self,attrs):
        try:
            SKU.objects.get(id = attrs)
        except SKU.DoesNotExist:
            raise serializers.ValidationError('商品不存在')
        return attrs

    def create(self, validated_data):
        sku_id = validated_data['sku_id']
        user_id = self.context['request'].user.id
        redis_conn = get_redis_connection('history')
        p1 = redis_conn.pipeline()
        p1.lrem('history_%s' %user_id,0,sku_id)
        p1.lpush('history_%s' %user_id,sku_id)
        #ltrim(key,起始位置，结束位置)  切割列表
        p1.ltrim('history_%s' %user_id,0,constants.USER_BROWSING_HISTORY_COUNTS_LIMIT-1)
        p1.execute()
        return validated_data

class SKUSerializer(serializers.ModelSerializer):
    class Meta:
        model = SKU
        fields = ['id','name','price','default_image_url','comments']









