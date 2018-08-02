import re
from django_redis import get_redis_connection
from rest_framework import serializers
from .models import User
from rest_framework_jwt.settings import api_settings
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