from decimal import Decimal, ROUND_HALF_UP
from django.db import transaction
from django.db.models import Q
from .models import  PackingMargins , CommodityMargin , MarketRates , BasicRates , PackSize , PackRates
from rest_framework import serializers


REFINED_COMMODITIES = {
    'soya refined',
    'mustard refined',
    'rice bran refined',
    'ricebran refined',
    'cottonseed refined',
}



class PackingMarginSerializer(serializers.ModelSerializer):
    class Meta:
        model = PackingMargins
        fields = ['id' , 'packing_name' , 'packing_margin' , 'created_by']

class CommodityMarginSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommodityMargin
        fields = ['id' ,'commodity' , 'margin_rate' , 'freight_rate' , 'created_by']

class MarketRateCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MarketRates
        fields = ['id' ,'commodity' , 'factory_kg' , 'created_by']

    @transaction.atomic
    def create(self, validated_data):
        market_rate = super().create(validated_data)

        commodity = market_rate.commodity
        if commodity and commodity.commodity.strip().lower() in REFINED_COMMODITIES:
            commodity_margin = commodity.margin_rate or Decimal('0')

            basic_price_by_packing = {
                packing.id: market_rate.factory_kg + commodity_margin + packing.packing_margin
                for packing in PackingMargins.objects.all()
            }

            BasicRates.objects.bulk_create([
                BasicRates(
                    packing_type_id=packing_id,
                    market_rate=market_rate,
                    basic_price_kg=basic_price,
                )
                for packing_id, basic_price in basic_price_by_packing.items()
            ])

            pack_sizes = PackSize.objects.filter(
                Q(commodities__isnull=True) | Q(commodities=commodity)
            ).distinct()

            PackRates.objects.bulk_create([
                PackRates(
                    market_rate=market_rate,
                    pack_size=pack_size,
                    rate=pack_size.rate_from_basic_kg(
                        basic_price_by_packing[pack_size.packing_id]
                    ).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
                )
                for pack_size in pack_sizes
                if pack_size.packing_id in basic_price_by_packing
            ])

        return market_rate

class MarketRatesViewSerializer(serializers.ModelSerializer):
    with_packing = serializers.ReadOnlyField() 
    with_gst_kg = serializers.ReadOnlyField()
    with_gst_ltr = serializers.ReadOnlyField() 

    freight_rate = serializers.SerializerMethodField()

    class Meta:
        model = MarketRates
        # Ensure you include all standard fields plus your computed fields
        fields = [
            'id', 
            'date',
            'commodity', 
            'factory_kg', 
            'factory_kg_freight',
            'with_packing', 
            'with_gst_kg', 
            'with_gst_ltr', 
            'freight_rate', 
            'created_by'
        ]

    def get_freight_rate(self, obj):
        # 'obj' is the MarketRates instance being serialized.
        # We access the freight_rate from the related commodity.
        if obj.commodity and hasattr(obj.commodity, 'freight_rate'):
            return obj.commodity.freight_rate
        
        # Return 0 or None if there is no related commodity or freight rate
        return 0

class BasicRatesSerializer(serializers.ModelSerializer):
    basic_price_ltr = serializers.ReadOnlyField()
    class Meta:
        model = BasicRates
        fields = '__all__'


class PackSizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PackSize
        fields = ['id', 'name', 'packing', 'unit', 'conversion_factor', 'commodities', 'display_order', 'created_by']


class PackRatesSerializer(serializers.ModelSerializer):
    pack_size_name = serializers.CharField(source='pack_size.name', read_only=True)
    commodity = serializers.CharField(source='market_rate.commodity.commodity', read_only=True)

    class Meta:
        model = PackRates
        fields = ['id', 'market_rate', 'pack_size', 'pack_size_name', 'commodity', 'rate', 'date']