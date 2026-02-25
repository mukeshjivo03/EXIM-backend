from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics

from .models import TankItem, TankData
from .serializers import TankItemSerializer, TankDataSerializer
from accounts.permissions import IsAdminUser , IsManagerUser , IsFactoryUser


class TankItemViews(generics.RetrieveUpdateDestroyAPIView):
    queryset = TankItem.objects.all()
    serializer_class = TankItemSerializer
    
