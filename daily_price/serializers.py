from rest_framework import serializers
from .models import DailyPrice

class DailyPriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyPrice
        fields = '__all__'
