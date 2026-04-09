from rest_framework import serializers
from .models import StockStatus , StockStatusUpdateLog , StockStatusFieldLog , StockStatusChangeSession 
from sap_sync.models import RMProducts , Party
from tank.models import TankData , TankItem



class StockStatusSerializer(serializers.ModelSerializer):
    
    item_code = serializers.SlugRelatedField(
        slug_field='tank_item_code', 
        queryset=TankItem.objects.all()
        
    )

    vendor_code = serializers.SlugRelatedField(
        slug_field='card_code',
        queryset=Party.objects.all()
    )

    eta = serializers.DateField(required=False, allow_null=True)

    class Meta:
        model = StockStatus
        fields = '__all__'
        read_only_fields = ['create_at' , 'total']

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


class StockStatusFieldLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockStatusFieldLog
        fields = ['field_name', 'old_value', 'new_value']

class StockStatusChangeSessionSerializer(serializers.ModelSerializer):
    field_logs = StockStatusFieldLogSerializer(many=True, read_only=True)
    
    class Meta:
        model = StockStatusChangeSession
        fields = ['id', 'stock', 'action', 'changed_by_label', 'note', 'timestamp', 'field_logs']