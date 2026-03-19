from rest_framework import serializers
from .models import DomesticReports

class DomesticReportSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = DomesticReports
        fields = '__all__'

