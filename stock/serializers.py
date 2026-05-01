from rest_framework import serializers
from .models import StockStatus , StockStatusUpdateLog , StockStatusFieldLog , StockStatusChangeSession , DebitEntry
from sap_sync.models import RMProducts , Party
from tank.models import TankData , TankItem



class StockStatusSerializer(serializers.ModelSerializer):
    
    item_code = serializers.SlugRelatedField(
        slug_field='tank_item_code', 
        queryset=TankItem.objects.all()
        
    )
    
    item_name = serializers.CharField(
        source='item_code.tank_item_name', 
        read_only=True
    )
        

    vendor_code = serializers.SlugRelatedField(
        slug_field='card_code',
        queryset=Party.objects.all()
    )
    
    vendor_name = serializers.CharField(
        source='vendor_code.card_name',
        read_only=True
    )

    eta = serializers.DateField(required=False, allow_null=True)

    class Meta:
        model = StockStatus
        fields = '__all__'
        read_only_fields = ['create_at' , 'total']
    
    # def validate(self, data):
    #     status = data.get('status') or (self.instance.status if self.instance else None)
    #     bility_number = data.get('bility_number') or (self.instance.bility_number if self.instance else None)
        
    #     contract_start = data.get('contract_start') or (self.instance.contract_start if self.instance else None)
    #     contract_end = data.get('contract_end') or (self.instance.contract_end if self.instance else None)

    #     if status == 'IN_TANK' and not bility_number:
    #         raise serializers.ValidationError("Bility number is required when status is IN_TANK.")
    #     if status == 'IN_CONTRACT' and not contract_start and not contract_end:
    #         raise serializers.ValidationError("Contract Start Date and Contract end date requires when status IN CONTRACT ")
    #     else:
    #         return data
        







class StockStatusUpdateLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockStatusUpdateLog
        fields = '__all__'




class StockStatusPatchSerializer(serializers.ModelSerializer):
    item_code = serializers.SlugRelatedField(
        slug_field='tank_item_code',
        queryset=TankItem.objects.all(),
        required=False  # ✅
    )
    vendor_code = serializers.SlugRelatedField(
        slug_field='card_code',
        queryset=Party.objects.all(),
        required=False  # ✅
    )
    status = serializers.ChoiceField(
        choices=StockStatus.STATUS_CHOICES,
        required=False  # ✅
    )
    eta = serializers.DateField(required=False, allow_null=True)

    class Meta:
        model = StockStatus
        fields = '__all__'
        read_only_fields = ['created_at', 'total']
        
    # def validate(self, data):
    #     status = data.get('status') or (self.instance.status if self.instance else None)
    #     bility_number = data.get('bility_number') or (self.instance.bility_number if self.instance else None)
        
    #     contract_start = data.get('contract_start') or (self.instance.contract_start if self.instance else None)
    #     contract_end = data.get('contract_end') or (self.instance.contract_end if self.instance else None)

    #     if status == 'IN_TANK' and not bility_number:
    #         raise serializers.ValidationError("Bility number is required when status is IN_TANK.")
    #     if status == 'IN_CONTRACT' and not contract_start and not contract_end:
    #         raise serializers.ValidationError("Contract Start Date and Contract end date requires when status IN CONTRACT ")
    #     else:
    #         return data

class StockStatusFieldLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockStatusFieldLog
        fields = ['field_name', 'old_value', 'new_value']


class StockStatusChangeSessionSerializer(serializers.ModelSerializer):
    field_logs = StockStatusFieldLogSerializer(many=True, read_only=True)
    
    class Meta:
        model = StockStatusChangeSession
        fields = ['id', 'stock', 'action', 'changed_by_label', 'note', 'timestamp', 'field_logs']
        
class DebitEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = DebitEntry
        fields = '__all__'
        read_only_fields = ['total', 'created_at' , 'allowed_shortage_qty' , 'deducted_shortage_qty' , 'deduction_amount' , 'shortage_qty']