from django.shortcuts import render

# Create your views here.
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response

from rest_framework.views import APIView
#这里必须使用这种导入方法！！！
from .models import User
from .serializers import CreateUserSerializer
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

