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
    item_code = serializers.SlugRelatedField(
        slug_field='tank_item_code', 
        queryset=TankItem.objects.all(),
        allow_null=True 
    )
        
    class Meta:
        model = TankData
        fields = '__all__'
        read_only_fields = ['created_at']
        
        
    def validate(self, data):
        tank_capacity = data.get('tank_capacity')
        current_capacity = data.get('current_capacity')
        item_code = data.get('item_code')
        
        if item_code is not None and current_capacity is None:
            raise serializers.ValidationError("Please also mention the Item Capacity")
        
        if current_capacity is not None and item_code is None:
            raise serializers.ValidationError("Please also mention the Item Code")
            
        
        if tank_capacity is not None and current_capacity is not None:
            if current_capacity > tank_capacity or current_capacity < 0 or tank_capacity < 0:
                raise serializers.ValidationError("Current or Tank capacity should be less than zero or more than tank capacity.")
            
        return data

class TankDataCapacitySerializer(serializers.ModelSerializer):
    
    item_code = serializers.SlugRelatedField(
        slug_field='tank_item_code', 
        queryset=TankItem.objects.all(),
        allow_null=True 
    )
    
    class Meta:
        model = TankData
        fields = ['current_capacity' , 'item_code']
        read_only_fields = ['created_at' , 'updated_at' ,'tank_number' ,'is_active' , 'tank_capacity']
        
    def validate(self, data):
        
        current_capacity = data.get('current_capacity')
        item_code = data.get('item_code')
        
        if item_code is not None and current_capacity is None:
            raise serializers.ValidationError("Please also mention the Item Capacity")
        
        if current_capacity is not None and item_code is None:
            raise serializers.ValidationError("Please also mention the Item Code")
            
            
        if self.instance and current_capacity is not None:
            if current_capacity > self.instance.tank_capacity or current_capacity < 0:
                raise serializers.ValidationError("Current capacity cannot be more than tanks capacity or less than zero.")
            
        return data