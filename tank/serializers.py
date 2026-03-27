from rest_framework import serializers
from .models import TankItem, TankData , TankLayer , TankLog , TankLogConsumption


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
        allow_null=True,
        required=False   
    )
        
    class Meta:
        model = TankData
        fields = '__all__'
        read_only_fields = ['created_at' , 'tank_code']
        
        
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
    
    
class TankInwardSerializer(serializers.Serializer):
    tank_code = serializers.CharField(max_length=20)
    stock_status_id = serializers.IntegerField()
    quantity = serializers.DecimalField(max_digits=10, decimal_places=2)
 
 
class TankOutwardSerializer(serializers.Serializer):
    tank_code = serializers.CharField(max_length=20)
    quantity = serializers.DecimalField(max_digits=10, decimal_places=2)
    remarks = serializers.CharField(required=False, default='', allow_blank=True)
 
 
class TankTransferSerializer(serializers.Serializer):
    source_tank_code = serializers.CharField(max_length=20)
    destination_tank_code = serializers.CharField(max_length=20)
    quantity = serializers.DecimalField(max_digits=10, decimal_places=2)
    remarks = serializers.CharField(required=False, default='', allow_blank=True)


class TankLayerResponseSerializer(serializers.ModelSerializer):
    rate = serializers.DecimalField(
        max_digits=10, decimal_places=2, source='stock_status.rate', read_only=True
    )
    vendor_name = serializers.CharField(
        source='stock_status.vendor_code.card_name', read_only=True, default='N/A'
    )
    item_name = serializers.CharField(
        source='stock_status.item_code.item_name', read_only=True, default='N/A'
    )
    stock_status_id = serializers.IntegerField(source='stock_status.id', read_only=True)
 
    class Meta:
        model = TankLayer
        fields = [
            'id', 'tank_code', 'stock_status_id',
            'rate', 'vendor_name', 'item_name',
            'quantity_added', 'quantity_remaining',
            'is_exhausted', 'created_at', 'created_by',
        ]
 
 
class TankLogConsumptionResponseSerializer(serializers.ModelSerializer):
    layer_id = serializers.IntegerField(source='tank_layer.id', read_only=True)
    vendor_name = serializers.CharField(
        source='tank_layer.stock_status.vendor_code.card_name', read_only=True, default='N/A'
    )
    stock_status_id = serializers.IntegerField(
        source='tank_layer.stock_status.id', read_only=True
    )
 
    class Meta:
        model = TankLogConsumption
        fields = [
            'id', 'layer_id', 'stock_status_id',
            'vendor_name', 'quantity_consumed', 'rate', 'created_at',
        ]
 
 
class TankLogResponseSerializer(serializers.ModelSerializer):
    consumptions = TankLogConsumptionResponseSerializer(many=True, read_only=True)
    stock_status_id = serializers.IntegerField(
        source='stock_status.id', read_only=True
    )
    tank_layer_id = serializers.IntegerField(
        source='tank_layer.id', read_only=True
    )
    source_tank_code = serializers.CharField(
        source='tank_code.tank_code', read_only=True
    )
    destination_tank_code = serializers.CharField(
        source='destination_tank.tank_code', read_only=True, default=None
    )

    class Meta:
        model = TankLog
        fields = [
            'id', 'log_type', 'quantity',
            'source_tank_code', 'destination_tank_code',
            'stock_status_id', 'tank_layer_id',
            'remarks', 'created_at', 'created_by',
            'consumptions',
        ]
 
class TankConsumptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TankLogConsumption
        fields = '__all__'
        read_only_fields = ['created_at']
        
class TankLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = TankLog
        fields = '__all__'
        read_only_fields = ['created_at']
        
class TransferTankSerialier(serializers.ModelSerializer):
    class Meta:
        model = TankData
        fields = ['tank_code' , 'item_code','current_capacity' ,'tank_capacity']
        
class TankLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = TankLog
        fields = '__all__'