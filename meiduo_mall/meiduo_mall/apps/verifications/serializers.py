from rest_framework import serializers
from django_redis import get_redis_connection


class CheckImageCodeSerializer(serializers.Serializer):
    image_code_id = serializers.UUIDField()
    text = serializers.CharField(max_length=4,min_length=4)

    def validate(self, attrs):
        #获取图片验证码标识和用户输入的图片验证码
        image_code_id = attrs['image_code_id']
        text = attrs['text']
        redis_conn = get_redis_connection('verify_codes')
        #判断60s之内是否发送过短信
        mobile = self.context['mobile']
        send_flag = redis_conn.get('send_flag_%s' %mobile)
        if send_flag:
            raise serializers.ValidationError('发送短信过于频繁')
        #与redis中图片验证码进行对比
        real_image_code = redis_conn.get('img_%s' %image_code_id)
        if not real_image_code:
            raise serializers.ValidationError('图片验证码无效')
        #讲redis中的图片验证码删除(防止重复使用)
        try:
            redis_conn.delete('img_%s' %image_code_id)
        except Exception as e:
            pass
        if text.lower()!=real_image_code.decode().lower():
            raise serializers.ValidationError('图片验证码错误')
        return attrs

