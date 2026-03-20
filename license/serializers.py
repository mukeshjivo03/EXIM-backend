from rest_framework import serializers
from .models import AdvanceLicenseHeaders, AdvanceLicenseLines , DFIALicenseHeader , DFIALicenseLines



class AdvanceLicenseLineSerialzer(serializers.ModelSerializer):
    class Meta:
        model = AdvanceLicenseLines
        fields = '__all__'
        
class AdvanceLicenseHeaderCreateSerialzer(serializers.ModelSerializer):
    lincense_lines = AdvanceLicenseLineSerialzer(many=True, read_only=True)
    class Meta:
        model = AdvanceLicenseHeaders
        fields = '__all__'
        read_only_fields = ['cif_value_usd' , 'fob_value_usd']

class AdvanceLicenseHeaderSerialzer(serializers.ModelSerializer):
    class Meta:
        model = AdvanceLicenseHeaders
        fields = '__all__'
        



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
        read_only_fields = ['cif_value_usd' , 'fob_value_usd']
        
        


            