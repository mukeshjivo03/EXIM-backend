from rest_framework import serializers
from .models import AdvanceLicenseHeaders, AdvanceLicenseLines


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
        