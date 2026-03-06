from rest_framework import generics
from rest_framework.views import APIView
from django_filters import rest_framework as filters
from rest_framework.response import Response
from django.db.models import Sum, Case, When, DecimalField, Value , Count
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
        queryset = StockStatus.objects.filter(deleted=False)
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

class StockDashboard(APIView):
    def get(self,request):
        dashboard = StockStatus.objects.filter(deleted=False).values('item_code').annotate(
            OUT_SIDE_FACTORY=Sum(Case(When(status='OUT_SIDE_FACTORY', then='quantity'), default=Value(0), output_field=DecimalField())),
            ON_THE_WAY=Sum(Case(When(status='ON_THE_WAY', then='quantity'), default=Value(0), output_field=DecimalField())),
            UNDER_LOADING=Sum(Case(When(status='UNDER_LOADING', then='quantity'), default=Value(0), output_field=DecimalField())),
            AT_REFINERY=Sum(Case(When(status='AT_REFINERY', then='quantity'), default=Value(0), output_field=DecimalField())),
            OTW_TO_REFINERY=Sum(Case(When(status='OTW_TO_REFINERY', then='quantity'), default=Value(0), output_field=DecimalField())),
            KANDLA_STORAGE=Sum(Case(When(status='KANDLA_STORAGE', then='quantity'), default=Value(0), output_field=DecimalField())),
            MUNDRA_PORT=Sum(Case(When(status='MUNDRA_PORT', then='quantity'), default=Value(0), output_field=DecimalField())),
            ON_THE_SEA=Sum(Case(When(status='ON_THE_SEA', then='quantity'), default=Value(0), output_field=DecimalField())),
            IN_CONTRACT=Sum(Case(When(status='IN_CONTRACT', then='quantity'), default=Value(0), output_field=DecimalField())),
            COMPLETED=Sum(Case(When(status='COMPLETED', then='quantity'), default=Value(0), output_field=DecimalField())),
            DELIVERED=Sum(Case(When(status='DELIVERED', then='quantity'), default=Value(0), output_field=DecimalField())),
            IN_TRANSIT=Sum(Case(When(status='IN_TRANSIT', then='quantity'), default=Value(0), output_field=DecimalField())),
            PENDING=Sum(Case(When(status='PENDING', then='quantity'), default=Value(0), output_field=DecimalField())),
            PROCESSING=Sum(Case(When(status='PROCESSING', then='quantity'), default=Value(0), output_field=DecimalField())),
            total_qty=Sum('quantity'),
        )
        return Response({
            "dashboard" : dashboard
        })