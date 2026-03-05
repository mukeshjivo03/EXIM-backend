from rest_framework import generics
from rest_framework.views import APIView
from django_filters import rest_framework as filters
from rest_framework.response import Response
from django.db.models import Sum, Count
from decimal import Decimal

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


  
class StockUpdateLogListView(generics.ListAPIView):
    queryset = StockStatusUpdateLog.objects.all()
    serializer_class = StockStatusUpdateLogSerializer
    permission_classes = [IsAdminUser]


class StockStatusInsights(APIView):
    
    def get(self, request):
        # Initial filter for non-deleted records
        queryset = StockStatus.objects.filter(deleted=False)
        
        # Apply filters from request.GET
        filterset = StockStatusFilters(request.GET, queryset=queryset)
        if filterset.is_valid():
            queryset = filterset.qs

        # FIXED: Use Count('id') for the total number of records
        insights = queryset.aggregate(
            total_value=Sum("total"),
            total_qty=Sum('quantity'),
            total_count=Count('id')
        )

        total_value = insights['total_value'] or Decimal('0.00')
        total_qty = insights['total_qty'] or Decimal('0.00')

        if total_qty > 0:
            avg_price_per_kg = round(total_value / total_qty, 2)
            # 1 litre of oil = 0.92 kg, so price_per_ltr = price_per_kg * 0.92
            avg_price_per_ltr = round(avg_price_per_kg * Decimal('0.92'), 2)
        else:
            avg_price_per_kg = Decimal('0.00')
            avg_price_per_ltr = Decimal('0.00')

        insights['avg_price_per_kg'] = avg_price_per_kg
        insights['avg_price_per_ltr'] = avg_price_per_ltr

        return Response({
            "summary": insights,
        })


class StockStatusSummary(APIView):

    def get(self, request):
        queryset = StockStatus.objects.filter(deleted=False)

        summary = queryset.aggregate(
            total_value=Sum("total"),
            total_qty=Sum('quantity'),
            total_count=Count('id')
        )

        total_value = summary['total_value'] or Decimal('0.00')
        total_qty = summary['total_qty'] or Decimal('0.00')

        if total_qty > 0:
            avg_price_per_kg = round(total_value / total_qty, 2)
            avg_price_per_ltr = round(avg_price_per_kg * Decimal('0.92'), 2)
        else:
            avg_price_per_kg = Decimal('0.00')
            avg_price_per_ltr = Decimal('0.00')

        summary['avg_price_per_kg'] = avg_price_per_kg
        summary['avg_price_per_ltr'] = avg_price_per_ltr

        return Response({
            "summary": summary,
        })