from rest_framework import serializers
from .models import TankItem, TankData

class TankItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = TankItem
        fields = '__all__'
        read_only_fields = ['created_at']
        
        

class TankItemColorSerialier(serializers.ModelSerializer):
    class Meta:
        model = TankItem
        fields = ['color' , 'tank_item_name']


class TankDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = TankData
        fields = '__all__'
        read_only_fields = ['created_at']
        
