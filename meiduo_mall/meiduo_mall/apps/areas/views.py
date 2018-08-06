from django.shortcuts import render

#请求省份数据
# GET /areas/
from rest_framework.generics import ListAPIView
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework_extensions.cache.mixins import CacheResponseMixin

from .serializers import AreaSerializer, SubAreaSerializer
from .models import Area

class AreaViewSet(CacheResponseMixin,ReadOnlyModelViewSet):
    pagination_class = None

    def get_queryset(self):
        if self.action == 'list':
            return Area.objects.filter(parent = None)
        else:
            return Area.objects.all()

    def get_serializer_class(self, *args, **kwargs):
        if self.action == 'list':
            return AreaSerializer
        else:
            return SubAreaSerializer
