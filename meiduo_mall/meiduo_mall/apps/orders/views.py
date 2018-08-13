from decimal import Decimal
from django_redis import get_redis_connection
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from goods.models import SKU
from .serializers import OrderSettlementSerializer, SaveOrderSerializer


# GET /orders/settlement/
class OrderSettlementView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request):
        redis_conn = get_redis_connection('cart')
        redis_cart = redis_conn.hgetall('cart_%s' %request.user.id)
        cart_selected = redis_conn.smembers('cart_selected_%s' %request.user.id)
        cart = {}
        for sku_id in cart_selected:
            count = int(redis_cart.get(sku_id))
            cart[int(sku_id)] = count
        skus = SKU.objects.filter(id__in = cart.keys())
        for sku in skus:
            sku.count = cart[sku.id]
        freight = Decimal('10.00')
        serializer = OrderSettlementSerializer({'freight':freight,'skus':skus})
        return Response(serializer.data)
# POST /orders/
class SaveOrderView(CreateAPIView):
    """
    保存订单
    """
    permission_classes = [IsAuthenticated]
    serializer_class = SaveOrderSerializer