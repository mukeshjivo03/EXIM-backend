from rest_framework import serializers
from .models import DomesticReports

class DomesticReportSerializer(serializers.modelSerializer):
    class Meta:
        mdoel = DomesticReports
        fields = '__all__'

