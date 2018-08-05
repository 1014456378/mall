from django.shortcuts import render

# Create your views here.
from rest_framework import status
from rest_framework.generics import CreateAPIView, RetrieveAPIView, UpdateAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
#这里必须使用这种导入方法！！！
from .models import User
from .serializers import CreateUserSerializer, UserDetailSerializer, EmailSerializer
from rest_framework.status import HTTP_201_CREATED



#判断用户名是否存在
# GET usernames/(?P<username>\w{5,20})/count/
class UsernameCountView(APIView):
    def get(self,request,username):
        count = User.objects.filter(username = username).count()
        data = {
            'username':username,
            'count':count
        }
        return Response(data)

#判断手机号是否存在
# GET mobiles/(?P<mobile>1[3-9]\d{9})/count/
class MobileCountView(APIView):
    def get(self,request,mobile):
        count = User.objects.filter(mobile=mobile).count()
        data = {
            'mobile':mobile,
            'count':count
        }
        return Response(data)

#注册接口
# POST /users/
class UserView(CreateAPIView):
    serializer_class = CreateUserSerializer

# 用户信息接口
# GET /user/
class UserDetailView(RetrieveAPIView):
    serializer_class = UserDetailSerializer
    permission_classes = [IsAuthenticated]
    def get_object(self,*args,**kwargs):
        return self.request.user

#发送验证邮件接口
# PUT /email/
class EmailView(UpdateAPIView):
    serializer_class = EmailSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self,*args,**kwargs):
        return self.request.user

#验证邮箱链接
#GET /emails/verification/?token=xxx
class VerifyEmailView(APIView):
    def get(self,request):
        token = request.query_params.get('token')
        if not token:
            return Response({'message':'缺少token'},status = status.HTTP_400_BAD_REQUEST)
        user = User.check_verify_email_token(token)
        if user is None:
            return Response({'message':'链接信息无效'},status = status.HTTP_400_BAD_REQUEST)
        else:
            user.email_active = True
            user.save()
            return Response({'message': 'OK'})



