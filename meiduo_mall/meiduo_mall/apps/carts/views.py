import base64
import pickle

from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django_redis import get_redis_connection

from . import constants
from goods.models import SKU
from .serializers import CartSerializer, CartSKUSerializer


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
            sku = SKU.objects.get(id = sku_id)
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
            print(redis_cart)
            redis_cart_selected = redis_conn.smembers('cart_select_%s' %user.id)
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