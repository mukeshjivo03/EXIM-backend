from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics

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
    
    