from django.shortcuts import render

# Create your views here.
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework_jwt.settings import api_settings
from itsdangerous import TimedJSONWebSignatureSerializer as TJWSSerializer

from carts.utils import merge_cart_cookie_to_redis
from .serializers import OAuthQQUserSerializer
from .models import OAuthQQUser
from oauth.exceptions import QQAPIError
from .utils import OAuthQQ

# GET /oauth/qq/authorization/?next=xxx
class QQAuthURLView(APIView):
    """获取QQ登陆网址"""
    def get(self,request):
        next = request.query_params.get('state','/')
        oauth = OAuthQQ(state = next)
        login_url = oauth.get_login_url()
        return Response({'login_url':login_url})


# GET /oauth/qq/user/?code=xxx
class QQAuthUserView(CreateAPIView):
    """获取qq用户的openid并进行处理"""
    serializer_class = OAuthQQUserSerializer
    def get(self,request):
        code = request.query_params.get('code')
        if not code:
            return Response({'message':'缺少code'},status=status.HTTP_400_BAD_REQUEST)
        try:
            oauth = OAuthQQ()
            access_token = oauth.get_access_token(code)
            openid = oauth.get_openid(access_token)
        except QQAPIError as e:
            return Response({'message':'QQ登陆异常'},status=status.HTTP_503_SERVICE_UNAVAILABLE)
        try:
            qq_user = OAuthQQUser.objects.get(openid = openid)
        except OAuthQQUser.DoesNotExist:
            token = OAuthQQ.generate_save_user_token(openid)
            return Response({'access_token':token})
        else:
            jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
            jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
            payload = jwt_payload_handler(qq_user.user)
            token = jwt_encode_handler(payload)
            response = Response({
                'token': token,
                'user_id': qq_user.user.id,
                'username': qq_user.user.username
            })
            response = merge_cart_cookie_to_redis(request, qq_user.user, response)
            return response

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        # 合并购物车
        response = merge_cart_cookie_to_redis(request, self.user, response)
        return response

