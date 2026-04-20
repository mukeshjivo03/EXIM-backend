from rest_framework import serializers
from .models import DomesticReports
from sap_sync.models import Party , RMProducts
from decimal import Decimal

class DomesticReportSerializer(serializers.ModelSerializer):
    product_name = serializers.SerializerMethodField()
    vendor_name = serializers.SerializerMethodField()

    def get_product_name(self, obj):
        try:
            return RMProducts.objects.get(item_code=obj.product_code).item_name
        except RMProducts.DoesNotExist:
            return None

    def get_vendor_name(self, obj):
        try:
            return Party.objects.get(card_code=obj.vendor_code).card_name
        except Party.DoesNotExist:
            return None

    class Meta:
        model = DomesticReports
        fields = '__all__'

    

class ContractSerializer(serializers.ModelSerializer):
    class Meta:
        model = DomesticReports
        fields = [
            'status', 'product_code', 'vendor_code',
            'po_number', 'po_date',
            'contract_qty', 'contract_rate', 'contract_total'
        ]
        read_only_fields = ['contract_total']

    def create(self, validated_data):
        validated_data['contract_total'] = (
            validated_data['contract_rate'] * validated_data['contract_qty']
        )
        return super().create(validated_data)
    
class LoadingSerializer(serializers.ModelSerializer):
    class Meta:
        model = DomesticReports
        fields = [
            'load_qty','unload_qty',
            
            'shortage','allow_shortage' , 'deduction_qty',
            'deduction_amount','basic_amount' 
        ]
        read_only_fields = ['basic_amount' , 'allow_shortage' , 'deduction_amount' , 'deduction_qty', 'shortage']

    def update(self, instance  , validated_data):
        load_qty = validated_data.get('load_qty' , instance.load_qty)
        unload_qty = validated_data.get('unload_qty' , instance.unload_qty)
        contract_rate = instance.contract_rate
        shortage = (load_qty - unload_qty) * 1000


        allowed_shortage = (Decimal('0.25') / 100 *load_qty) * 1000
        deduction_qty = shortage - allowed_shortage

        if deduction_qty < 0:
            deduction_qty = 0
            deduction_amount = 0 
        else:
            deduction_amount = (deduction_qty / 1000)*contract_rate


        validated_data['basic_amount'] = load_qty * contract_rate
        validated_data['allow_shortage'] = allowed_shortage
        validated_data['deduction_amount'] = deduction_amount
        validated_data['deduction_qty'] = deduction_qty
        validated_data['shortage'] = shortage

        return super().update(instance, validated_data)


class FreightSerializer(serializers.ModelSerializer):
    class Meta:
        model = DomesticReports
        fields = [
            'transporter_code' , 'transporter_name' ,
            'bility_number' , 'bility_date' ,
            'grpo_date' , 'grpo_number' ,

            'brokerage_amount' ,'freight_amount' ,
            'frieght_rate',

            'vehicle_number' , 'invoice_number']

        read_only_fields = ['freight_amount']

    def to_internal_value(self, data):
        # Accept both 'freight_rate' (correct spelling) and 'frieght_rate' (legacy DB spelling)
        mutable = data.copy() if hasattr(data, 'copy') else dict(data)
        if 'freight_rate' in mutable and 'frieght_rate' not in mutable:
            mutable['frieght_rate'] = mutable.pop('freight_rate')
        return super().to_internal_value(mutable)

    def update(self, instance, validated_data):
        frieght_rate = validated_data.get('frieght_rate', instance.frieght_rate or 0)
        unload_qty = instance.unload_qty or 0
        validated_data['freight_amount'] = Decimal(str(unload_qty)) * Decimal(str(frieght_rate))
        return super().update(instance, validated_data)


class ContractDropdownSerializer(serializers.ModelSerializer):
    product_name = serializers.SerializerMethodField()
    vendor_name = serializers.SerializerMethodField()
    
    def get_product_name(self, obj):
        try :
            product = RMProducts.objects.get(item_code=obj.product_code)
            return product.item_name
        except RMProducts.DoesNotExist:
            return None
        
    def get_vendor_name(self, obj):
        try:
            party = Party.objects.get(card_code=obj.vendor_code)
            return party.card_name
        except Party.DoesNotExist:
            return None
        
    class Meta:
        model = DomesticReports
        fields = ['id' , 'po_number' , 'vendor_code' ,'vendor_name' ,'product_code' , 'product_name']
