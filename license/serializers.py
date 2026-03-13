from rest_framework import serializers
from .models import AdvanceLicenseHeaders, AdvanceLicenseLines , DFIALicenseHeader , DFIALicenseLines



class AdvanceLicenseLineSerialzer(serializers.ModelSerializer):
    class Meta:
        model = AdvanceLicenseLines
        fields = '__all__'
        
class AdvanceLicenseHeaderSerialzer(serializers.ModelSerializer):
    lincense_lines = AdvanceLicenseLineSerialzer(many=True, read_only=True)
    class Meta:
        model = AdvanceLicenseHeaders
        fields = '__all__'
        read_only_fields = ['cif_value_usd' , 'fob_value_usd']
        

class DFIALicenseLineSerializer(serializers.ModelSerializer):
    class Meta:
        model = DFIALicenseLines
        fields = '__all__'
        
        

class DFIALicenseListSerializer(serializers.ModelSerializer):
    dfia_license_lines = DFIALicenseLineSerializer(many=True, read_only=True)
    class Meta:
        model = DFIALicenseHeader
        fields = '__all__'


class DFIALicenseheaderCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DFIALicenseHeader
        fields = '__all__'
        
    def __init__(self , *args , **kwargs):
        super().__init__(*args , **kwargs)
        
        data = kwargs.get('data')
        
        if data.get('fob_value_inr') and data.get('fob_exchange_rate'):
            self.fields['fob_value_usd'].read_only = True
            self.fields['fob_value_usd'].required = False
            
        elif data.get('fob_value_usd') and data.get('fob_exchange_rate'):
            self.fields['fob_value_inr'].read_only = True
            self.fields['fob_value_inr'].required = False   
            
        if data.get('cif_value_inr') and data.get('cif_exchange_rate'):
            self.fields['cif_value_usd'].read = True
            self.fields['cif_value_usd'].required = False
            
        elif data.get('cif_value_usd') and data.get('cif_exchange_rate'):
            self.fields['cif_value_inr'].read_only = True
            self.fields['cif_value_inr'].required = False
            