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
        final_capacity = data.get('current_capacity', getattr(self.instance, 'current_capacity', None))
        final_item = data.get('item_code', getattr(self.instance, 'item_code', None))
        max_capacity = data.get('tank_capacity', getattr(self.instance, 'tank_capacity', None))

        if final_capacity == 0 and final_item is None:
            pass # This is perfectly fine!
        
        else:
            if final_item is not None and final_capacity in [None, 0]:
                raise serializers.ValidationError({"current_capacity": "You cannot assign an item without a capacity greater than 0."})

            if final_capacity is not None and final_capacity > 0 and final_item is None:
                raise serializers.ValidationError({"item_code": "You cannot add capacity without assigning an Item Code."})

        if final_capacity is not None and max_capacity is not None:
            if final_capacity > max_capacity:
                raise serializers.ValidationError({"current_capacity": f"Cannot exceed tank capacity of {max_capacity}."})
            if final_capacity < 0:
                raise serializers.ValidationError({"current_capacity": "Capacity cannot be negative."})

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
        final_capacity = data.get('current_capacity', getattr(self.instance, 'current_capacity', None))
        final_item = data.get('item_code', getattr(self.instance, 'item_code', None))
        max_capacity = data.get('tank_capacity', getattr(self.instance, 'tank_capacity', None))

        if final_capacity == 0 and final_item is None:
            pass # This is perfectly fine!
        
        else:
            if final_item is not None and final_capacity in [None, 0]:
                raise serializers.ValidationError({"current_capacity": "You cannot assign an item without a capacity greater than 0."})
            if final_capacity is not None and final_capacity > 0 and final_item is None:
                raise serializers.ValidationError({"item_code": "You cannot add capacity without assigning an Item Code."})

        if final_capacity is not None and max_capacity is not None:
            if final_capacity > max_capacity:
                raise serializers.ValidationError({"current_capacity": f"Cannot exceed tank capacity of {max_capacity}."})
            if final_capacity < 0:
                raise serializers.ValidationError({"current_capacity": "Capacity cannot be negative."})

        return data