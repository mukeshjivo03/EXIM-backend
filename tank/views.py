from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Sum, Count
from decimal import Decimal

from .models import TankItem, TankData
from .serializers import TankItemSerializer, TankDataSerializer , TankItemColorSerialier ,TankDataCapacitySerializer
from accounts.permissions import IsAdminUser , IsManagerUser , IsFactoryUser


    
# TANK DATA VIEWS
  
class TankDataView(generics.RetrieveDestroyAPIView):
    queryset = TankData.objects.all()
    serializer_class = TankDataSerializer
    lookup_field = 'tank_code'
    
    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAuthenticated()]
        
        return [IsAdminUser()]


class TankDataListCrateView(generics.ListCreateAPIView):
    queryset = TankData.objects.all()
    serializer_class = TankDataSerializer
    
    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAuthenticated()]
        
        return [IsAdminUser()]
    
class TankCapacityUpdateView(generics.UpdateAPIView):
    queryset = TankData.objects.all()
    serializer_class = TankDataCapacitySerializer
    lookup_field = 'tank_code'
    
    

# TANK ITEM VIEWS
class TankItemViews(generics.RetrieveDestroyAPIView):
    queryset = TankItem.objects.all()
    serializer_class = TankItemSerializer
    lookup_field = 'tank_item_code'
    
    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAuthenticated()]
        
        return [IsAdminUser()]
    
class TankItemListCreateView(generics.ListCreateAPIView):
    queryset = TankItem.objects.all()
    serializer_class = TankItemSerializer
    
    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAuthenticated()]
        
        return [IsAdminUser()]
   
class TankItemColorUpdateView(generics.UpdateAPIView):
    queryset = TankItem.objects.all()
    serializer_class = TankItemColorSerialier
    lookup_field = 'tank_item_code'


class TankDataSummary(APIView):

    def get(self, request):
        queryset = TankData.objects.filter(is_active=True)

        data = queryset.aggregate(
            total_tank_capacity=Sum('tank_capacity'),
            current_stock=Sum('current_capacity'),
            tank_count=Count('tank_code'),
            item_count=Count('item_code', distinct=True)
        )

        total_tank_capacity = data['total_tank_capacity'] or Decimal('0.00')
        current_stock = data['current_stock'] or Decimal('0.00')

        if total_tank_capacity > 0:
            utilisation_rate = round((current_stock / total_tank_capacity) * 100, 2)
        else:
            utilisation_rate = Decimal('0.00')

        return Response({
            "summary": {
                "total_tank_capacity": total_tank_capacity,
                "current_stock": current_stock,
                "utilisation_rate": utilisation_rate,
                "tank_count": data['tank_count'],
                "item_count": data['item_count'],
            }
        })


class TankItemWiseSummary(APIView):

    def get(self, request):
        queryset = TankData.objects.filter(is_active=True, item_code__isnull=False)

        item_data = queryset.values(
            'item_code__tank_item_code',
            'item_code__tank_item_name',
            'item_code__color'
        ).annotate(
            quantity_in_liters=Sum('current_capacity'),
            total_capacity=Sum('tank_capacity'),
            tank_count=Count('tank_code')
        )

        results = []
        for item in item_data:
            tank_codes = list(
                queryset.filter(item_code=item['item_code__tank_item_code'])
                .values_list('tank_code', flat=True)
            )
            results.append({
                "color": item['item_code__color'],
                "tank_item_code": item['item_code__tank_item_code'],
                "tank_item_name": item['item_code__tank_item_name'],
                "quantity_in_liters": item['quantity_in_liters'] or Decimal('0.00'),
                "total_capacity": item['total_capacity'] or Decimal('0.00'),
                "tank_count": item['tank_count'],
                "tank_numbers": tank_codes,
            })

        return Response(results)