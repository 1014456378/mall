from django.shortcuts import render

# Create your views here.
from drf_haystack.viewsets import HaystackViewSet

from rest_framework.filters import OrderingFilter
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import SKU
from .serializers import SKUSerializer, SKUIndexSerializer


# GET /categories/(?P<category_id>\d+)/skus?page=xxx&page_size=xxx&ordering=xxx
class SKUListView(ListAPIView):
    """
    sku列表数据
    """
    serializer_class = SKUSerializer
    filter_backends = (OrderingFilter,)
    ordering_fields = ('create_time', 'price', 'sales')

    def get_queryset(self):
        category_id = self.kwargs['category_id']
        return SKU.objects.filter(category_id=category_id, is_launched=True)

# GET /categories/(?P<category_id>\d+)/hotskus/
class SKUHot(APIView):
    """商品热销排行"""
    def get(self,request,category_id):
        hot_list = SKU.objects.filter(is_launched = True,category_id = category_id).order_by('-sales')[:5]
        serializers = SKUSerializer(hot_list,many=True)
        return Response(serializers.data)


class SKUSearchViewSet(HaystackViewSet):
    index_models = [SKU]
    serializer_class = SKUIndexSerializer
