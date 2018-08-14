import base64
import pickle

from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django_redis import get_redis_connection

from . import constants
from goods.models import SKU
from .serializers import CartSerializer, CartSKUSerializer, CartDeleteSerializer, CartSelectAllSerializer


# /cart/
class CartView(APIView):
    def perform_authentication(self, request):
        pass

    def post(self,request):
        serializer = CartSerializer(data = request.data)
        serializer.is_valid(raise_exception=True)
        sku_id = serializer.data['sku_id']
        count = serializer.data['count']
        selected = serializer.data['selected']

        try:
            user = request.user
        except Exception:
            user = None

        if user is not None and user.is_authenticated:
            redis_conn = get_redis_connection('cart')
            p1 = redis_conn.pipeline()
            p1.hincrby('cart_%s' %user.id,sku_id,count)
            if selected:
                p1.sadd('cart_selected_%s' %user.id,sku_id)
            p1.execute()
            return Response(serializer.data,status = status.HTTP_201_CREATED)
        else:
            cart = request.COOKIES.get('cart')
            if cart is not None:
                cart = pickle.loads(base64.b64decode(cart.encode()))
            else:
                cart = {}

            if sku_id in cart:
                count +=cart['sku_id']['count']

            cart[sku_id] = {
                'count':count,
                'selected':selected
            }
            cookie_cart = base64.b64encode(pickle.dumps(cart)).decode()
            response = Response(serializer.data,status = status.HTTP_201_CREATED)
            response.set_cookie('cart',cookie_cart,max_age=constants.CART_COOKIE_EXPIRES)
            return response
    def get(self,request):
        try:
            user = request.user
        except:
            user = None
        if user is not None and user.is_authenticated:
            redis_conn = get_redis_connection('cart')
            redis_cart = redis_conn.hgetall('cart_%s' %user.id)
            redis_cart_selected = redis_conn.smembers('cart_selected_%s' %user.id)
            cart = {}

            for sku_id,count in redis_cart.items():
                cart[int(sku_id)] = {
                    'count':int(count),
                    'selected':sku_id in redis_cart_selected
                }
        else:
            cart = request.COOKIES.get('cart')
            if cart is not None:
                cart = pickle.loads(base64.b64decode(cart.encode()))
            else:
                cart = {}
        skus = SKU.objects.filter(id__in=cart.keys())
        for sku in skus:
            sku.count = cart[sku.id]['count']
            sku.selected = cart[sku.id]['selected']
        serializer = CartSKUSerializer(skus,many=True)
        return Response(serializer.data)
    def put(self,request):
        serializer = CartSerializer(data = request.data)
        serializer.is_valid(raise_exception=True)
        sku_id = serializer.data['sku_id']
        count = serializer.data['count']
        selected = serializer.data['selected']
        try:
            user = request.user
        except:
            user = None
        if user is not None and user.is_authenticated:
            redis_conn = get_redis_connection('cart')
            p1 = redis_conn.pipeline()
            p1.hset('cart_%s' %user.id,sku_id,count)
            if selected:
                p1.sadd('cart_selected_%s' %user.id,sku_id)
            else:
                p1.srem('cart_selected_%s' %user.id,sku_id)
            p1.execute()
            return Response(serializer.data)
        else:
            cart = request.COOKIES.get('cart')
            if cart is not None:
                cart = pickle.loads(base64.b64decode(cart.encode()))
            else:
                cart = {}
            cart[sku_id]['count'] = count
            cart[sku_id]['selected'] = selected
            cart_c = base64.b64encode(pickle.dumps(cart)).decode()
            response = Response(serializer.data)
            response.set_cookie('cart',cart_c,max_age=constants.CART_COOKIE_EXPIRES)
            return response
    def delete(self,request):
        serializer = CartDeleteSerializer(data = request.data)
        serializer.is_valid(raise_exception=True)
        sku_id = serializer.data['sku_id']
        try:
            user = request.user
        except:
            user = None
        if user is not None and user.is_authenticated:
            redis_conn = get_redis_connection('cart')
            p1 = redis_conn.pipeline()
            p1.hdel('cart_%s' %user.id,sku_id)
            p1.srem('cart_selected_%s' %user.id,sku_id)
            p1.execute()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            response = Response(status=status.HTTP_204_NO_CONTENT)

            # 使用pickle序列化购物车数据，pickle操作的是bytes类型
            cart = request.COOKIES.get('cart')
            if cart is not None:
                cart = pickle.loads(base64.b64decode(cart.encode()))
                if sku_id in cart:
                    del cart[sku_id]
                    cookie_cart = base64.b64encode(pickle.dumps(cart)).decode()
                    # 设置购物车的cookie
                    # 需要设置有效期，否则是临时cookie
                    response.set_cookie('cart', cookie_cart, max_age=constants.CART_COOKIE_EXPIRES)
            return response

# PUT /cart/selection/
class CartSelectAllView(APIView):
    """
    购物车全选
    """
    def perform_authentication(self, request):
        pass

    def put(self,request):
        serializer = CartSelectAllSerializer(data = request.data)
        serializer.is_valid(raise_exception=True)
        selected = serializer.data['selected']
        try:
            user = request.user
        except:
            user = None
        if user is not None:
            redis_conn = get_redis_connection('cart')
            cart_all = redis_conn.hgetall('cart_%s' %user.id)
            if selected:
                redis_conn.sadd('cart_selected_%s' %user.id,*cart_all.keys())
            else:
                redis_conn.srem('cart_selected_%s' %user.id,*cart_all.keys())
            return Response({'message':'OK'})
        else:
            cart = request.COOKIES.get('cart')
            response =Response({'message':'OK'})
            if cart is not None:
                cart = pickle.loads(base64.b64decode(cart.encode()))
                for sku_id in cart:
                    cart[sku_id]['selected'] = selected
                cart_c = base64.b64encode(pickle.dumps(cart)).decode()
                response.set_cookie('cart',cart_c,max_age=constants.CART_COOKIE_EXPIRES)
            return response












