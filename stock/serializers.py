from rest_framework import serializers
from .models import StockStatus , StockStatusUpdateLog
from sap_sync.models import RMProducts , Party


class StockStatusSerializer(serializers.ModelSerializer):

    item_code = serializers.SlugRelatedField(
        slug_field='item_code', 
        queryset=RMProducts.objects.all()
    )

    vendor_code = serializers.SlugRelatedField(
        slug_field='card_code', 
        queryset=Party.objects.all()
    )

    class Meta:
        model = StockStatus
        fields = '__all__'
        read_only_fields = ['create_at' , 'total']

class StockStatusUpdateLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockStatusUpdateLog
        fields = '__all__'