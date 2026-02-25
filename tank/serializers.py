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
        
class TankDataCapacitySerializer(serializers.ModelSerializer):
    
    item_code = serializers.SlugRelatedField(
        slug_field='tank_item_code', 
        queryset=TankItem.objects.all(),
        allow_null=True 
    )
    
    class Meta:
        model = TankData
        fields = ['current_capacity' , 'item_code']