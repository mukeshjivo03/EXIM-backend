from rest_framework import generics
from rest_framework.views import APIView
from django_filters import rest_framework as filters
from rest_framework.response import Response
from django.db.models import Sum, Count

from .models import StockStatus ,StockStatusUpdateLog
from .serializers import StockStatusSerializer , StockStatusUpdateLogSerializer
from accounts.permissions import IsAdminUser , IsFactoryUser , IsManagerUser
from .filters import StockStatusFilters


class StockStatusListCreateView(generics.ListCreateAPIView):
    queryset = StockStatus.objects.filter(deleted=False)
    serializer_class = StockStatusSerializer
    permission_classes = [IsAdminUser]
    filter_backends = (filters.DjangoFilterBackend,) 
    filterset_class = StockStatusFilters


class StockStatusUpdateRetrieveDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = StockStatus.objects.all()
    serializer_class = StockStatusSerializer
    permission_classes = [IsAdminUser]
    lookup_field =  'id'

class StockUpdateLogListView(generics.ListAPIView):
    queryset = StockStatusUpdateLog.objects.all()
    serializer_class = StockStatusUpdateLogSerializer
    permission_classes = [IsAdminUser]

class StockStatusInsights(APIView):
    
    def get(self, request):
        # Apply the deleted filter first
        queryset = StockStatus.objects.filter(deleted=False)
        
        filterset = StockStatusFilters(request.GET, queryset=queryset)
        if filterset.is_valid():
            queryset = filterset.qs

        insights = queryset.aggregate(
            total_value=Sum("total"), 
            total_qty=Sum('quantity'), 
            total_count=Count('id')
        )

        status_distribution = queryset.values('status').annotate(
            value=Sum('total'), 
            count=Count('id')
        )

        item_distribution = queryset.values('item_code__code').annotate(
            value=Sum('total'), 
            count=Count('id')
        )

        vendor_distribution = queryset.values('vendor_code__code').annotate(
            value=Sum('total'), 
            count=Count('id')
        )

        return Response({
            "summary": insights,
            "status-chart": status_distribution,
            "item-chart": item_distribution,
            "vendor_chart": vendor_distribution
        })