from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics

from .models import TankItem, TankData
from .serializers import TankItemSerializer, TankDataSerializer , TankItemColorSerialier
from accounts.permissions import IsAdminUser , IsManagerUser , IsFactoryUser


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