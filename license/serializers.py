from rest_framework import serializers
from .models import AdvanceLicenseHeaders, AdvanceLicenseImportLines , AdvanceLicenseExportLines , DFIALicenseHeader , DFIALicenseLines


class AdvanceLicenseImportLine(serializers.ModelSerializer):
    class Meta:
        model = AdvanceLicenseImportLines
        fields = '__all__'
    
class AdvanceLicenseExportLine(serializers.ModelSerializer):
    class Meta:
        model = AdvanceLicenseExportLines
        fields = '__all__'  
    
           
class AdvanceLicenseHeaderCreateSerialzer(serializers.ModelSerializer):
    import_lines = AdvanceLicenseImportLine(many=True, read_only=True)
    export_lines = AdvanceLicenseExportLine(many=True, read_only=True)
    
    class Meta:
        model = AdvanceLicenseHeaders
        fields = '__all__'
        read_only_fields = ['cif_value_usd' , 'fob_value_usd' , 'total_import' , 'to_be_exported' , 'total_export' , 'balance']



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
        
        


            