from rest_framework import serializers
from .models import AdvanceLicenseHeaders, AdvanceLicenseImportLines , AdvanceLicenseExportLines , DFIALicenseHeader , DFIALicenseExportLines , DFIALicenseImportLines

    
class AdvanceLicenseImportLine(serializers.ModelSerializer):
    class Meta:
        model = AdvanceLicenseImportLines
        fields = '__all__'
    
class AdvanceLicenseExportLine(serializers.ModelSerializer):
    linked_import_line = AdvanceLicenseImportLine(read_only=True)
    class Meta:
        model = AdvanceLicenseExportLines
        fields = '__all__'  
    
           
class AdvanceLicenseHeaderCreateSerialzer(serializers.ModelSerializer):
    import_lines = AdvanceLicenseImportLine(many=True, read_only=True)
    export_lines = AdvanceLicenseExportLine(many=True, read_only=True)
    
    class Meta:
        model = AdvanceLicenseHeaders
        fields = '__all__'
        read_only_fields = ['cif_value_usd' , 'fob_value_usd' , 'total_import' , 'to_be_exported' , 'total_export' , 'balance' , 'total_to_be_exported_quantity']



class AdvanceLicenseHeaderSerialzer(serializers.ModelSerializer):
    class Meta:
        model = AdvanceLicenseHeaders
        fields = '__all__'
        







class DFIAExportLines(serializers.ModelSerializer):
    class Meta:
        model = DFIALicenseExportLines
        fields = '__all__'
        
class DFIAImportLines(serializers.ModelSerializer):
    linked_export_line = DFIAExportLines(read_only=True)
    linked_export_line_id = serializers.PrimaryKeyRelatedField(
        queryset=DFIALicenseExportLines.objects.all(),
        source='linked_export_line',
        required=False,
        allow_null=True,
    )

    class Meta:
        model = DFIALicenseImportLines
        fields = '__all__'


class DFIALicenseListSerializer(serializers.ModelSerializer):
    dfia_import_lines = DFIAImportLines(many=True, read_only=True)
    dfia_export_lines = DFIAExportLines(many=True, read_only=True)
    class Meta:
        model = DFIALicenseHeader
        fields = '__all__'


class DFIALicenseheaderCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DFIALicenseHeader
        fields = '__all__'
        read_only_fields = ['cif_value_usd' , 'fob_value_usd' , 'total_import' , 'to_be_imported' , 'total_export' , 'balance']
        
        


            