from rest_framework import serializers
from .models import AdvanceLicenseHeaders, AdvanceLicenseImportLines , AdvanceLicenseExportLines , DFIALicenseHeader , DFIALicenseExportLines , DFIALicenseImportLines


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
        





class DFIAImportLines(serializers.ModelSerializer):
    class Meta:
        model = DFIALicenseImportLines
        fields = '__all__'

class DFIAExportLines(serializers.ModelSerializer):
    class Meta:
        model = DFIALicenseExportLines
        fields = '__all__'
        


class DFIALicenseListSerializer(serializers.ModelSerializer):
    dfia_import_lines = DFIAImportLines(many=True, read_only=True)
    dfia__export_lines = DFIAExportLines(many=True, read_only=True)
    class Meta:
        model = DFIALicenseHeader
        fields = '__all__'


class DFIALicenseheaderCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DFIALicenseHeader
        fields = '__all__'
        read_only_fields = ['cif_value_usd' , 'fob_value_usd' , 'total_import' , 'to_be_imported' , 'total_export' , 'balance']
        
        


            