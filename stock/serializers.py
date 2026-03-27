from rest_framework import serializers
from .models import StockStatus , StockStatusUpdateLog
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

